class BaseHistGradientBoosting(BaseEstimator, ABC):
    """Base class for histogram-based gradient boosting estimators."""

    _parameter_constraints: dict = {
        "loss": [BaseLoss],
        "learning_rate": [Interval(Real, 0, None, closed="neither")],
        "max_iter": [Interval(Integral, 1, None, closed="left")],
        "max_leaf_nodes": [Interval(Integral, 2, None, closed="left"), None],
        "max_depth": [Interval(Integral, 1, None, closed="left"), None],
        "min_samples_leaf": [Interval(Integral, 1, None, closed="left")],
        "l2_regularization": [Interval(Real, 0, None, closed="left")],
        "max_features": [Interval(RealNotInt, 0, 1, closed="right")],
        "monotonic_cst": ["array-like", dict, None],
        "interaction_cst": [
            list,
            tuple,
            StrOptions({"pairwise", "no_interactions"}),
            None,
        ],
        "n_iter_no_change": [Interval(Integral, 1, None, closed="left")],
        "validation_fraction": [
            Interval(RealNotInt, 0, 1, closed="neither"),
            Interval(Integral, 1, None, closed="left"),
            None,
        ],
        "tol": [Interval(Real, 0, None, closed="left")],
        "max_bins": [Interval(Integral, 2, 255, closed="both")],
        "categorical_features": [
            "array-like",
            StrOptions({"from_dtype"}),
            Hidden(StrOptions({"warn"})),
            None,
        ],
        "warm_start": ["boolean"],
        "early_stopping": [StrOptions({"auto"}), "boolean"],
        "scoring": [str, callable, None],
        "verbose": ["verbose"],
        "random_state": ["random_state"],
    }

    @abstractmethod
    def __init__(
        self,
        loss,
        *,
        learning_rate,
        max_iter,
        max_leaf_nodes,
        max_depth,
        min_samples_leaf,
        l2_regularization,
        max_features,
        max_bins,
        categorical_features,
        monotonic_cst,
        interaction_cst,
        warm_start,
        early_stopping,
        scoring,
        validation_fraction,
        n_iter_no_change,
        tol,
        verbose,
        random_state,
    ):
        self.loss = loss
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.max_leaf_nodes = max_leaf_nodes
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.l2_regularization = l2_regularization
        self.max_features = max_features
        self.max_bins = max_bins
        self.monotonic_cst = monotonic_cst
        self.interaction_cst = interaction_cst
        self.categorical_features = categorical_features
        self.warm_start = warm_start
        self.early_stopping = early_stopping
        self.scoring = scoring
        self.validation_fraction = validation_fraction
        self.n_iter_no_change = n_iter_no_change
        self.tol = tol
        self.verbose = verbose
        self.random_state = random_state

    def _validate_parameters(self):
        """Validate parameters passed to __init__.

        The parameters that are directly passed to the grower are checked in
        TreeGrower."""
        if self.monotonic_cst is not None and self.n_trees_per_iteration_ != 1:
            raise ValueError(
                "monotonic constraints are not supported for multiclass classification."
            )

    def _finalize_sample_weight(self, sample_weight, y):
        """Finalize sample weight.

        Used by subclasses to adjust sample_weights. This is useful for implementing
        class weights.
        """
        return sample_weight

    def _preprocess_X(self, X, *, reset):
        """Preprocess and validate X.

        Parameters
        ----------
        X : {array-like, pandas DataFrame} of shape (n_samples, n_features)
            Input data.

        reset : bool
            Whether to reset the `n_features_in_` and `feature_names_in_ attributes.

        Returns
        -------
        X : ndarray of shape (n_samples, n_features)
            Validated input data.

        known_categories : list of ndarray of shape (n_categories,)
            List of known categories for each categorical feature.
        """
        # If there is a preprocessor, we let the preprocessor handle the validation.
        # Otherwise, we validate the data ourselves.
        check_X_kwargs = dict(dtype=[X_DTYPE], force_all_finite=False)
        if not reset:
            if self._preprocessor is None:
                return self._validate_data(X, reset=False, **check_X_kwargs)
            return self._preprocessor.transform(X)

        # At this point, reset is False, which runs during `fit`.
        self.is_categorical_ = self._check_categorical_features(X)

        if self.is_categorical_ is None:
            self._preprocessor = None
            self._is_categorical_remapped = None

            X = self._validate_data(X, **check_X_kwargs)
            return X, None

        n_features = X.shape[1]
        ordinal_encoder = OrdinalEncoder(
            categories="auto",
            handle_unknown="use_encoded_value",
            unknown_value=np.nan,
            encoded_missing_value=np.nan,
            dtype=X_DTYPE,
        )

        check_X = partial(check_array, **check_X_kwargs)
        numerical_preprocessor = FunctionTransformer(check_X)
        self._preprocessor = ColumnTransformer(
            [
                ("encoder", ordinal_encoder, self.is_categorical_),
                ("numerical", numerical_preprocessor, ~self.is_categorical_),
            ]
        )
        self._preprocessor.set_output(transform="default")
        X = self._preprocessor.fit_transform(X)
        # check categories found by the OrdinalEncoder and get their encoded values
        known_categories = self._check_categories()
        self.n_features_in_ = self._preprocessor.n_features_in_
        with suppress(AttributeError):
            self.feature_names_in_ = self._preprocessor.feature_names_in_

        # The ColumnTransformer's output places the categorical features at the
        # beginning
        categorical_remapped = np.zeros(n_features, dtype=bool)
        categorical_remapped[self._preprocessor.output_indices_["encoder"]] = True
        self._is_categorical_remapped = categorical_remapped

        return X, known_categories

    def _check_categories(self):
        """Check categories found by the preprocessor and return their encoded values.

        Returns a list of length ``self.n_features_in_``, with one entry per
        input feature.

        For non-categorical features, the corresponding entry is ``None``.

        For categorical features, the corresponding entry is an array
        containing the categories as encoded by the preprocessor (an
        ``OrdinalEncoder``), excluding missing values. The entry is therefore
        ``np.arange(n_categories)`` where ``n_categories`` is the number of
        unique values in the considered feature column, after removing missing
        values.

        If ``n_categories > self.max_bins`` for any feature, a ``ValueError``
        is raised.
        """
        encoder = self._preprocessor.named_transformers_["encoder"]
        known_categories = [None] * self._preprocessor.n_features_in_
        categorical_column_indices = np.arange(self._preprocessor.n_features_in_)[
            self._preprocessor.output_indices_["encoder"]
        ]
        for feature_idx, categories in zip(
            categorical_column_indices, encoder.categories_
        ):
            # OrdinalEncoder always puts np.nan as the last category if the
            # training data has missing values. Here we remove it because it is
            # already added by the _BinMapper.
            if len(categories) and is_scalar_nan(categories[-1]):
                categories = categories[:-1]
            if categories.size > self.max_bins:
                try:
                    feature_name = repr(encoder.feature_names_in_[feature_idx])
                except AttributeError:
                    feature_name = f"at index {feature_idx}"
                raise ValueError(
                    f"Categorical feature {feature_name} is expected to "
                    f"have a cardinality <= {self.max_bins} but actually "
                    f"has a cardinality of {categories.size}."
                )
            known_categories[feature_idx] = np.arange(len(categories), dtype=X_DTYPE)
        return known_categories

    def _check_categorical_features(self, X):
        """Check and validate categorical features in X

        Parameters
        ----------
        X : {array-like, pandas DataFrame} of shape (n_samples, n_features)
            Input data.

        Return
        ------
        is_categorical : ndarray of shape (n_features,) or None, dtype=bool
            Indicates whether a feature is categorical. If no feature is
            categorical, this is None.
        """
        # Special code for pandas because of a bug in recent pandas, which is
        # fixed in main and maybe included in 2.2.1, see
        # https://github.com/pandas-dev/pandas/pull/57173.
        # Also pandas versions < 1.5.1 do not support the dataframe interchange
        if _is_pandas_df(X):
            X_is_dataframe = True
            categorical_columns_mask = np.asarray(X.dtypes == "category")
            X_has_categorical_columns = categorical_columns_mask.any()
        elif hasattr(X, "__dataframe__"):
            X_is_dataframe = True
            categorical_columns_mask = np.asarray(
                [
                    c.dtype[0].name == "CATEGORICAL"
                    for c in X.__dataframe__().get_columns()
                ]
            )
            X_has_categorical_columns = categorical_columns_mask.any()
        else:
            X_is_dataframe = False
            categorical_columns_mask = None
            X_has_categorical_columns = False

        # TODO(1.6): Remove warning and change default to "from_dtype" in v1.6
        if (
            isinstance(self.categorical_features, str)
            and self.categorical_features == "warn"
        ):
            if X_has_categorical_columns:
                warnings.warn(
                    (
                        "The categorical_features parameter will change to 'from_dtype'"
                        " in v1.6. The 'from_dtype' option automatically treats"
                        " categorical dtypes in a DataFrame as categorical features."
                    ),
                    FutureWarning,
                )
            categorical_features = None
        else:
            categorical_features = self.categorical_features

        categorical_by_dtype = (
            isinstance(categorical_features, str)
            and categorical_features == "from_dtype"
        )
        no_categorical_dtype = categorical_features is None or (
            categorical_by_dtype and not X_is_dataframe
        )

        if no_categorical_dtype:
            return None

        use_pandas_categorical = categorical_by_dtype and X_is_dataframe
        if use_pandas_categorical:
            categorical_features = categorical_columns_mask
        else:
            categorical_features = np.asarray(categorical_features)

        if categorical_features.size == 0:
            return None

        if categorical_features.dtype.kind not in ("i", "b", "U", "O"):
            raise ValueError(
                "categorical_features must be an array-like of bool, int or "
                f"str, got: {categorical_features.dtype.name}."
            )

        if categorical_features.dtype.kind == "O":
            types = set(type(f) for f in categorical_features)
            if types != {str}:
                raise ValueError(
                    "categorical_features must be an array-like of bool, int or "
                    f"str, got: {', '.join(sorted(t.__name__ for t in types))}."
                )

        n_features = X.shape[1]
        # At this point `_validate_data` was not called yet because we want to use the
        # dtypes are used to discover the categorical features. Thus `feature_names_in_`
        # is not defined yet.
        feature_names_in_ = getattr(X, "columns", None)

        if categorical_features.dtype.kind in ("U", "O"):
            # check for feature names
            if feature_names_in_ is None:
                raise ValueError(
                    "categorical_features should be passed as an array of "
                    "integers or as a boolean mask when the model is fitted "
                    "on data without feature names."
                )
            is_categorical = np.zeros(n_features, dtype=bool)
            feature_names = list(feature_names_in_)
            for feature_name in categorical_features:
                try:
                    is_categorical[feature_names.index(feature_name)] = True
                except ValueError as e:
                    raise ValueError(
                        f"categorical_features has a item value '{feature_name}' "
                        "which is not a valid feature name of the training "
                        f"data. Observed feature names: {feature_names}"
                    ) from e
        elif categorical_features.dtype.kind == "i":
            # check for categorical features as indices
            if (
                np.max(categorical_features) >= n_features
                or np.min(categorical_features) < 0
            ):
                raise ValueError(
                    "categorical_features set as integer "
                    "indices must be in [0, n_features - 1]"
                )
            is_categorical = np.zeros(n_features, dtype=bool)
            is_categorical[categorical_features] = True
        else:
            if categorical_features.shape[0] != n_features:
                raise ValueError(
                    "categorical_features set as a boolean mask "
                    "must have shape (n_features,), got: "
                    f"{categorical_features.shape}"
                )
            is_categorical = categorical_features

        if not np.any(is_categorical):
            return None
        return is_categorical

    def _check_interaction_cst(self, n_features):
        """Check and validation for interaction constraints."""
        if self.interaction_cst is None:
            return None

        if self.interaction_cst == "no_interactions":
            interaction_cst = [[i] for i in range(n_features)]
        elif self.interaction_cst == "pairwise":
            interaction_cst = itertools.combinations(range(n_features), 2)
        else:
            interaction_cst = self.interaction_cst

        try:
            constraints = [set(group) for group in interaction_cst]
        except TypeError:
            raise ValueError(
                "Interaction constraints must be a sequence of tuples or lists, got:"
                f" {self.interaction_cst!r}."
            )

        for group in constraints:
            for x in group:
                if not (isinstance(x, Integral) and 0 <= x < n_features):
                    raise ValueError(
                        "Interaction constraints must consist of integer indices in"
                        f" [0, n_features - 1] = [0, {n_features - 1}], specifying the"
                        " position of features, got invalid indices:"
                        f" {group!r}"
                    )

        # Add all not listed features as own group by default.
        rest = set(range(n_features)) - set().union(*constraints)
        if len(rest) > 0:
            constraints.append(rest)

        return constraints

    @_fit_context(prefer_skip_nested_validation=True)
    def fit(self, X, y, sample_weight=None):
        """Fit the gradient boosting model.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The input samples.

        y : array-like of shape (n_samples,)
            Target values.

        sample_weight : array-like of shape (n_samples,) default=None
            Weights of training data.

            .. versionadded:: 0.23

        Returns
        -------
        self : object
            Fitted estimator.
        """
        fit_start_time = time()
        acc_find_split_time = 0.0  # time spent finding the best splits
        acc_apply_split_time = 0.0  # time spent splitting nodes
        acc_compute_hist_time = 0.0  # time spent computing histograms
        # time spent predicting X for gradient and hessians update
        acc_prediction_time = 0.0
        X, known_categories = self._preprocess_X(X, reset=True)
        y = _check_y(y, estimator=self)
        y = self._encode_y(y)
        check_consistent_length(X, y)
        # Do not create unit sample weights by default to later skip some
        # computation
        if sample_weight is not None:
            sample_weight = _check_sample_weight(sample_weight, X, dtype=np.float64)
            # TODO: remove when PDP supports sample weights
            self._fitted_with_sw = True

        sample_weight = self._finalize_sample_weight(sample_weight, y)

        rng = check_random_state(self.random_state)

        # When warm starting, we want to reuse the same seed that was used
        # the first time fit was called (e.g. train/val split).
        # For feature subsampling, we want to continue with the rng we started with.
        if not self.warm_start or not self._is_fitted():
            self._random_seed = rng.randint(np.iinfo(np.uint32).max, dtype="u8")
            feature_subsample_seed = rng.randint(np.iinfo(np.uint32).max, dtype="u8")
            self._feature_subsample_rng = np.random.default_rng(feature_subsample_seed)

        self._validate_parameters()
        monotonic_cst = _check_monotonic_cst(self, self.monotonic_cst)

        # used for validation in predict
        n_samples, self._n_features = X.shape

        # Encode constraints into a list of sets of features indices (integers).
        interaction_cst = self._check_interaction_cst(self._n_features)

        # we need this stateful variable to tell raw_predict() that it was
        # called from fit() (this current method), and that the data it has
        # received is pre-binned.
        # predicting is faster on pre-binned data, so we want early stopping
        # predictions to be made on pre-binned data. Unfortunately the _scorer
        # can only call predict() or predict_proba(), not raw_predict(), and
        # there's no way to tell the scorer that it needs to predict binned
        # data.
        self._in_fit = True

        # `_openmp_effective_n_threads` is used to take cgroups CPU quotes
        # into account when determine the maximum number of threads to use.
        n_threads = _openmp_effective_n_threads()

        if isinstance(self.loss, str):
            self._loss = self._get_loss(sample_weight=sample_weight)
        elif isinstance(self.loss, BaseLoss):
            self._loss = self.loss

        if self.early_stopping == "auto":
            self.do_early_stopping_ = n_samples > 10000
        else:
            self.do_early_stopping_ = self.early_stopping

        # create validation data if needed
        self._use_validation_data = self.validation_fraction is not None
        if self.do_early_stopping_ and self._use_validation_data:
            # stratify for classification
            # instead of checking predict_proba, loss.n_classes >= 2 would also work
            stratify = y if hasattr(self._loss, "predict_proba") else None

            # Save the state of the RNG for the training and validation split.
            # This is needed in order to have the same split when using
            # warm starting.

            if sample_weight is None:
                X_train, X_val, y_train, y_val = train_test_split(
                    X,
                    y,
                    test_size=self.validation_fraction,
                    stratify=stratify,
                    random_state=self._random_seed,
                )
                sample_weight_train = sample_weight_val = None
            else:
                # TODO: incorporate sample_weight in sampling here, as well as
                # stratify
                (
                    X_train,
                    X_val,
                    y_train,
                    y_val,
                    sample_weight_train,
                    sample_weight_val,
                ) = train_test_split(
                    X,
                    y,
                    sample_weight,
                    test_size=self.validation_fraction,
                    stratify=stratify,
                    random_state=self._random_seed,
                )
        else:
            X_train, y_train, sample_weight_train = X, y, sample_weight
            X_val = y_val = sample_weight_val = None

        # Bin the data
        # For ease of use of the API, the user-facing GBDT classes accept the
        # parameter max_bins, which doesn't take into account the bin for
        # missing values (which is always allocated). However, since max_bins
        # isn't the true maximal number of bins, all other private classes
        # (binmapper, histbuilder...) accept n_bins instead, which is the
        # actual total number of bins. Everywhere in the code, the
        # convention is that n_bins == max_bins + 1
        n_bins = self.max_bins + 1  # + 1 for missing values
        self._bin_mapper = _BinMapper(
            n_bins=n_bins,
            is_categorical=self._is_categorical_remapped,
            known_categories=known_categories,
            random_state=self._random_seed,
            n_threads=n_threads,
        )
        X_binned_train = self._bin_data(X_train, is_training_data=True)
        if X_val is not None:
            X_binned_val = self._bin_data(X_val, is_training_data=False)
        else:
            X_binned_val = None

        # Uses binned data to check for missing values
        has_missing_values = (
            (X_binned_train == self._bin_mapper.missing_values_bin_idx_)
            .any(axis=0)
            .astype(np.uint8)
        )

        if self.verbose:
            print("Fitting gradient boosted rounds:")

        n_samples = X_binned_train.shape[0]
        scoring_is_predefined_string = self.scoring in _SCORERS
        need_raw_predictions_val = X_binned_val is not None and (
            scoring_is_predefined_string or self.scoring == "loss"
        )
        # First time calling fit, or no warm start
        if not (self._is_fitted() and self.warm_start):
            # Clear random state and score attributes
            self._clear_state()

            # initialize raw_predictions: those are the accumulated values
            # predicted by the trees for the training data. raw_predictions has
            # shape (n_samples, n_trees_per_iteration) where
            # n_trees_per_iterations is n_classes in multiclass classification,
            # else 1.
            # self._baseline_prediction has shape (1, n_trees_per_iteration)
            self._baseline_prediction = self._loss.fit_intercept_only(
                y_true=y_train, sample_weight=sample_weight_train
            ).reshape((1, -1))
            raw_predictions = np.zeros(
                shape=(n_samples, self.n_trees_per_iteration_),
                dtype=self._baseline_prediction.dtype,
                order="F",
            )
            raw_predictions += self._baseline_prediction

            # predictors is a matrix (list of lists) of TreePredictor objects
            # with shape (n_iter_, n_trees_per_iteration)
            self._predictors = predictors = []

            # Initialize structures and attributes related to early stopping
            self._scorer = None  # set if scoring != loss
            raw_predictions_val = None  # set if use val and scoring is a string
            self.train_score_ = []
            self.validation_score_ = []

            if self.do_early_stopping_:
                # populate train_score and validation_score with the
                # predictions of the initial model (before the first tree)

                # Create raw_predictions_val for storing the raw predictions of
                # the validation data.
                if need_raw_predictions_val:
                    raw_predictions_val = np.zeros(
                        shape=(X_binned_val.shape[0], self.n_trees_per_iteration_),
                        dtype=self._baseline_prediction.dtype,
                        order="F",
                    )

                    raw_predictions_val += self._baseline_prediction

                if self.scoring == "loss":
                    # we're going to compute scoring w.r.t the loss. As losses
                    # take raw predictions as input (unlike the scorers), we
                    # can optimize a bit and avoid repeating computing the
                    # predictions of the previous trees. We'll reuse
                    # raw_predictions (as it's needed for training anyway) for
                    # evaluating the training loss.

                    self._check_early_stopping_loss(
                        raw_predictions=raw_predictions,
                        y_train=y_train,
                        sample_weight_train=sample_weight_train,
                        raw_predictions_val=raw_predictions_val,
                        y_val=y_val,
                        sample_weight_val=sample_weight_val,
                        n_threads=n_threads,
                    )
                else:
                    self._scorer = check_scoring(self, self.scoring)
                    # _scorer is a callable with signature (est, X, y) and
                    # calls est.predict() or est.predict_proba() depending on
                    # its nature.
                    # Unfortunately, each call to _scorer() will compute
                    # the predictions of all the trees. So we use a subset of
                    # the training set to compute train scores.

                    # Compute the subsample set
                    (
                        X_binned_small_train,
                        y_small_train,
                        sample_weight_small_train,
                        indices_small_train,
                    ) = self._get_small_trainset(
                        X_binned_train,
                        y_train,
                        sample_weight_train,
                        self._random_seed,
                    )

                    # If the scorer is a predefined string, then we optimize
                    # the evaluation by re-using the incrementally updated raw
                    # predictions.
                    if scoring_is_predefined_string:
                        raw_predictions_small_train = raw_predictions[
                            indices_small_train
                        ]
                    else:
                        raw_predictions_small_train = None

                    self._check_early_stopping_scorer(
                        X_binned_small_train,
                        y_small_train,
                        sample_weight_small_train,
                        X_binned_val,
                        y_val,
                        sample_weight_val,
                        raw_predictions_small_train=raw_predictions_small_train,
                        raw_predictions_val=raw_predictions_val,
                    )
            begin_at_stage = 0

        # warm start: this is not the first time fit was called
        else:
            # Check that the maximum number of iterations is not smaller
            # than the number of iterations from the previous fit
            if self.max_iter < self.n_iter_:
                raise ValueError(
                    "max_iter=%d must be larger than or equal to "
                    "n_iter_=%d when warm_start==True" % (self.max_iter, self.n_iter_)
                )

            # Convert array attributes to lists
            self.train_score_ = self.train_score_.tolist()
            self.validation_score_ = self.validation_score_.tolist()

            # Compute raw predictions
            raw_predictions = self._raw_predict(X_binned_train, n_threads=n_threads)
            if self.do_early_stopping_ and need_raw_predictions_val:
                raw_predictions_val = self._raw_predict(
                    X_binned_val, n_threads=n_threads
                )
            else:
                raw_predictions_val = None

            if self.do_early_stopping_ and self.scoring != "loss":
                # Compute the subsample set
                (
                    X_binned_small_train,
                    y_small_train,
                    sample_weight_small_train,
                    indices_small_train,
                ) = self._get_small_trainset(
                    X_binned_train, y_train, sample_weight_train, self._random_seed
                )

            # Get the predictors from the previous fit
            predictors = self._predictors

            begin_at_stage = self.n_iter_

        # initialize gradients and hessians (empty arrays).
        # shape = (n_samples, n_trees_per_iteration).
        gradient, hessian = self._loss.init_gradient_and_hessian(
            n_samples=n_samples, dtype=G_H_DTYPE, order="F"
        )

        for iteration in range(begin_at_stage, self.max_iter):
            if self.verbose:
                iteration_start_time = time()
                print(
                    "[{}/{}] ".format(iteration + 1, self.max_iter), end="", flush=True
                )

            # Update gradients and hessians, inplace
            # Note that self._loss expects shape (n_samples,) for
            # n_trees_per_iteration = 1 else shape (n_samples, n_trees_per_iteration).
            if self._loss.constant_hessian:
                self._loss.gradient(
                    y_true=y_train,
                    raw_prediction=raw_predictions,
                    sample_weight=sample_weight_train,
                    gradient_out=gradient,
                    n_threads=n_threads,
                )
            else:
                self._loss.gradient_hessian(
                    y_true=y_train,
                    raw_prediction=raw_predictions,
                    sample_weight=sample_weight_train,
                    gradient_out=gradient,
                    hessian_out=hessian,
                    n_threads=n_threads,
                )

            # Append a list since there may be more than 1 predictor per iter
            predictors.append([])

            # 2-d views of shape (n_samples, n_trees_per_iteration_) or (n_samples, 1)
            # on gradient and hessian to simplify the loop over n_trees_per_iteration_.
            if gradient.ndim == 1:
                g_view = gradient.reshape((-1, 1))
                h_view = hessian.reshape((-1, 1))
            else:
                g_view = gradient
                h_view = hessian

            # Build `n_trees_per_iteration` trees.
            for k in range(self.n_trees_per_iteration_):
                grower = TreeGrower(
                    X_binned=X_binned_train,
                    gradients=g_view[:, k],
                    hessians=h_view[:, k],
                    n_bins=n_bins,
                    n_bins_non_missing=self._bin_mapper.n_bins_non_missing_,
                    has_missing_values=has_missing_values,
                    is_categorical=self._is_categorical_remapped,
                    monotonic_cst=monotonic_cst,
                    interaction_cst=interaction_cst,
                    max_leaf_nodes=self.max_leaf_nodes,
                    max_depth=self.max_depth,
                    min_samples_leaf=self.min_samples_leaf,
                    l2_regularization=self.l2_regularization,
                    feature_fraction_per_split=self.max_features,
                    rng=self._feature_subsample_rng,
                    shrinkage=self.learning_rate,
                    n_threads=n_threads,
                )
                grower.grow()

                acc_apply_split_time += grower.total_apply_split_time
                acc_find_split_time += grower.total_find_split_time
                acc_compute_hist_time += grower.total_compute_hist_time

                if not self._loss.differentiable:
                    _update_leaves_values(
                        loss=self._loss,
                        grower=grower,
                        y_true=y_train,
                        raw_prediction=raw_predictions[:, k],
                        sample_weight=sample_weight_train,
                    )

                predictor = grower.make_predictor(
                    binning_thresholds=self._bin_mapper.bin_thresholds_
                )
                predictors[-1].append(predictor)

                # Update raw_predictions with the predictions of the newly
                # created tree.
                tic_pred = time()
                _update_raw_predictions(raw_predictions[:, k], grower, n_threads)
                toc_pred = time()
                acc_prediction_time += toc_pred - tic_pred

            should_early_stop = False
            if self.do_early_stopping_:
                # Update raw_predictions_val with the newest tree(s)
                if need_raw_predictions_val:
                    for k, pred in enumerate(self._predictors[-1]):
                        raw_predictions_val[:, k] += pred.predict_binned(
                            X_binned_val,
                            self._bin_mapper.missing_values_bin_idx_,
                            n_threads,
                        )

                if self.scoring == "loss":
                    should_early_stop = self._check_early_stopping_loss(
                        raw_predictions=raw_predictions,
                        y_train=y_train,
                        sample_weight_train=sample_weight_train,
                        raw_predictions_val=raw_predictions_val,
                        y_val=y_val,
                        sample_weight_val=sample_weight_val,
                        n_threads=n_threads,
                    )

                else:
                    # If the scorer is a predefined string, then we optimize the
                    # evaluation by re-using the incrementally computed raw predictions.
                    if scoring_is_predefined_string:
                        raw_predictions_small_train = raw_predictions[
                            indices_small_train
                        ]
                    else:
                        raw_predictions_small_train = None

                    should_early_stop = self._check_early_stopping_scorer(
                        X_binned_small_train,
                        y_small_train,
                        sample_weight_small_train,
                        X_binned_val,
                        y_val,
                        sample_weight_val,
                        raw_predictions_small_train=raw_predictions_small_train,
                        raw_predictions_val=raw_predictions_val,
                    )

            if self.verbose:
                self._print_iteration_stats(iteration_start_time)

            # maybe we could also early stop if all the trees are stumps?
            if should_early_stop:
                break

        if self.verbose:
            duration = time() - fit_start_time
            n_total_leaves = sum(
                predictor.get_n_leaf_nodes()
                for predictors_at_ith_iteration in self._predictors
                for predictor in predictors_at_ith_iteration
            )
            n_predictors = sum(
                len(predictors_at_ith_iteration)
                for predictors_at_ith_iteration in self._predictors
            )
            print(
                "Fit {} trees in {:.3f} s, ({} total leaves)".format(
                    n_predictors, duration, n_total_leaves
                )
            )
            print(
                "{:<32} {:.3f}s".format(
                    "Time spent computing histograms:", acc_compute_hist_time
                )
            )
            print(
                "{:<32} {:.3f}s".format(
                    "Time spent finding best splits:", acc_find_split_time
                )
            )
            print(
                "{:<32} {:.3f}s".format(
                    "Time spent applying splits:", acc_apply_split_time
                )
            )
            print(
                "{:<32} {:.3f}s".format("Time spent predicting:", acc_prediction_time)
            )

        self.train_score_ = np.asarray(self.train_score_)
        self.validation_score_ = np.asarray(self.validation_score_)
        del self._in_fit  # hard delete so we're sure it can't be used anymore
        return self

    def _is_fitted(self):
        return len(getattr(self, "_predictors", [])) > 0

    def _clear_state(self):
        """Clear the state of the gradient boosting model."""
        for var in ("train_score_", "validation_score_"):
            if hasattr(self, var):
                delattr(self, var)

    def _get_small_trainset(self, X_binned_train, y_train, sample_weight_train, seed):
        """Compute the indices of the subsample set and return this set.

        For efficiency, we need to subsample the training set to compute scores
        with scorers.
        """
        # TODO: incorporate sample_weights here in `resample`
        subsample_size = 10000
        if X_binned_train.shape[0] > subsample_size:
            indices = np.arange(X_binned_train.shape[0])
            stratify = y_train if is_classifier(self) else None
            indices = resample(
                indices,
                n_samples=subsample_size,
                replace=False,
                random_state=seed,
                stratify=stratify,
            )
            X_binned_small_train = X_binned_train[indices]
            y_small_train = y_train[indices]
            if sample_weight_train is not None:
                sample_weight_small_train = sample_weight_train[indices]
            else:
                sample_weight_small_train = None
            X_binned_small_train = np.ascontiguousarray(X_binned_small_train)
            return (
                X_binned_small_train,
                y_small_train,
                sample_weight_small_train,
                indices,
            )
        else:
            return X_binned_train, y_train, sample_weight_train, slice(None)

    def _check_early_stopping_scorer(
        self,
        X_binned_small_train,
        y_small_train,
        sample_weight_small_train,
        X_binned_val,
        y_val,
        sample_weight_val,
        raw_predictions_small_train=None,
        raw_predictions_val=None,
    ):
        """Check if fitting should be early-stopped based on scorer.

        Scores are computed on validation data or on training data.
        """
        if is_classifier(self):
            y_small_train = self.classes_[y_small_train.astype(int)]

        self.train_score_.append(
            self._score_with_raw_predictions(
                X_binned_small_train,
                y_small_train,
                sample_weight_small_train,
                raw_predictions_small_train,
            )
        )

        if self._use_validation_data:
            if is_classifier(self):
                y_val = self.classes_[y_val.astype(int)]
            self.validation_score_.append(
                self._score_with_raw_predictions(
                    X_binned_val, y_val, sample_weight_val, raw_predictions_val
                )
            )
            return self._should_stop(self.validation_score_)
        else:
            return self._should_stop(self.train_score_)

    def _score_with_raw_predictions(self, X, y, sample_weight, raw_predictions=None):
        if raw_predictions is None:
            patcher_raw_predict = nullcontext()
        else:
            patcher_raw_predict = _patch_raw_predict(self, raw_predictions)

        with patcher_raw_predict:
            if sample_weight is None:
                return self._scorer(self, X, y)
            else:
                return self._scorer(self, X, y, sample_weight=sample_weight)

    def _check_early_stopping_loss(
        self,
        raw_predictions,
        y_train,
        sample_weight_train,
        raw_predictions_val,
        y_val,
        sample_weight_val,
        n_threads=1,
    ):
        """Check if fitting should be early-stopped based on loss.

        Scores are computed on validation data or on training data.
        """
        self.train_score_.append(
            -self._loss(
                y_true=y_train,
                raw_prediction=raw_predictions,
                sample_weight=sample_weight_train,
                n_threads=n_threads,
            )
        )

        if self._use_validation_data:
            self.validation_score_.append(
                -self._loss(
                    y_true=y_val,
                    raw_prediction=raw_predictions_val,
                    sample_weight=sample_weight_val,
                    n_threads=n_threads,
                )
            )
            return self._should_stop(self.validation_score_)
        else:
            return self._should_stop(self.train_score_)

    def _should_stop(self, scores):
        """
        Return True (do early stopping) if the last n scores aren't better
        than the (n-1)th-to-last score, up to some tolerance.
        """
        reference_position = self.n_iter_no_change + 1
        if len(scores) < reference_position:
            return False

        # A higher score is always better. Higher tol means that it will be
        # harder for subsequent iteration to be considered an improvement upon
        # the reference score, and therefore it is more likely to early stop
        # because of the lack of significant improvement.
        reference_score = scores[-reference_position] + self.tol
        recent_scores = scores[-reference_position + 1 :]
        recent_improvements = [score > reference_score for score in recent_scores]
        return not any(recent_improvements)

    def _bin_data(self, X, is_training_data):
        """Bin data X.

        If is_training_data, then fit the _bin_mapper attribute.
        Else, the binned data is converted to a C-contiguous array.
        """

        description = "training" if is_training_data else "validation"
        if self.verbose:
            print(
                "Binning {:.3f} GB of {} data: ".format(X.nbytes / 1e9, description),
                end="",
                flush=True,
            )
        tic = time()
        if is_training_data:
            X_binned = self._bin_mapper.fit_transform(X)  # F-aligned array
        else:
            X_binned = self._bin_mapper.transform(X)  # F-aligned array
            # We convert the array to C-contiguous since predicting is faster
            # with this layout (training is faster on F-arrays though)
            X_binned = np.ascontiguousarray(X_binned)
        toc = time()
        if self.verbose:
            duration = toc - tic
            print("{:.3f} s".format(duration))

        return X_binned

    def _print_iteration_stats(self, iteration_start_time):
        """Print info about the current fitting iteration."""
        log_msg = ""

        predictors_of_ith_iteration = [
            predictors_list
            for predictors_list in self._predictors[-1]
            if predictors_list
        ]
        n_trees = len(predictors_of_ith_iteration)
        max_depth = max(
            predictor.get_max_depth() for predictor in predictors_of_ith_iteration
        )
        n_leaves = sum(
            predictor.get_n_leaf_nodes() for predictor in predictors_of_ith_iteration
        )

        if n_trees == 1:
            log_msg += "{} tree, {} leaves, ".format(n_trees, n_leaves)
        else:
            log_msg += "{} trees, {} leaves ".format(n_trees, n_leaves)
            log_msg += "({} on avg), ".format(int(n_leaves / n_trees))

        log_msg += "max depth = {}, ".format(max_depth)

        if self.do_early_stopping_:
            if self.scoring == "loss":
                factor = -1  # score_ arrays contain the negative loss
                name = "loss"
            else:
                factor = 1
                name = "score"
            log_msg += "train {}: {:.5f}, ".format(name, factor * self.train_score_[-1])
            if self._use_validation_data:
                log_msg += "val {}: {:.5f}, ".format(
                    name, factor * self.validation_score_[-1]
                )

        iteration_time = time() - iteration_start_time
        log_msg += "in {:0.3f}s".format(iteration_time)

        print(log_msg)

    def _raw_predict(self, X, n_threads=None):
        """Return the sum of the leaves values over all predictors.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The input samples.
        n_threads : int, default=None
            Number of OpenMP threads to use. `_openmp_effective_n_threads` is called
            to determine the effective number of threads use, which takes cgroups CPU
            quotes into account. See the docstring of `_openmp_effective_n_threads`
            for details.

        Returns
        -------
        raw_predictions : array, shape (n_samples, n_trees_per_iteration)
            The raw predicted values.
        """
        check_is_fitted(self)
        is_binned = getattr(self, "_in_fit", False)
        if not is_binned:
            X = self._preprocess_X(X, reset=False)

        n_samples = X.shape[0]
        raw_predictions = np.zeros(
            shape=(n_samples, self.n_trees_per_iteration_),
            dtype=self._baseline_prediction.dtype,
            order="F",
        )
        raw_predictions += self._baseline_prediction

        # We intentionally decouple the number of threads used at prediction
        # time from the number of threads used at fit time because the model
        # can be deployed on a different machine for prediction purposes.
        n_threads = _openmp_effective_n_threads(n_threads)
        self._predict_iterations(
            X, self._predictors, raw_predictions, is_binned, n_threads
        )
        return raw_predictions

    def _predict_iterations(self, X, predictors, raw_predictions, is_binned, n_threads):
        """Add the predictions of the predictors to raw_predictions."""
        if not is_binned:
            (
                known_cat_bitsets,
                f_idx_map,
            ) = self._bin_mapper.make_known_categories_bitsets()

        for predictors_of_ith_iteration in predictors:
            for k, predictor in enumerate(predictors_of_ith_iteration):
                if is_binned:
                    predict = partial(
                        predictor.predict_binned,
                        missing_values_bin_idx=self._bin_mapper.missing_values_bin_idx_,
                        n_threads=n_threads,
                    )
                else:
                    predict = partial(
                        predictor.predict,
                        known_cat_bitsets=known_cat_bitsets,
                        f_idx_map=f_idx_map,
                        n_threads=n_threads,
                    )
                raw_predictions[:, k] += predict(X)

    def _staged_raw_predict(self, X):
        """Compute raw predictions of ``X`` for each iteration.

        This method allows monitoring (i.e. determine error on testing set)
        after each stage.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The input samples.

        Yields
        ------
        raw_predictions : generator of ndarray of shape \
            (n_samples, n_trees_per_iteration)
            The raw predictions of the input samples. The order of the
            classes corresponds to that in the attribute :term:`classes_`.
        """
        check_is_fitted(self)
        X = self._preprocess_X(X, reset=False)
        if X.shape[1] != self._n_features:
            raise ValueError(
                "X has {} features but this estimator was trained with "
                "{} features.".format(X.shape[1], self._n_features)
            )
        n_samples = X.shape[0]
        raw_predictions = np.zeros(
            shape=(n_samples, self.n_trees_per_iteration_),
            dtype=self._baseline_prediction.dtype,
            order="F",
        )
        raw_predictions += self._baseline_prediction

        # We intentionally decouple the number of threads used at prediction
        # time from the number of threads used at fit time because the model
        # can be deployed on a different machine for prediction purposes.
        n_threads = _openmp_effective_n_threads()
        for iteration in range(len(self._predictors)):
            self._predict_iterations(
                X,
                self._predictors[iteration : iteration + 1],
                raw_predictions,
                is_binned=False,
                n_threads=n_threads,
            )
            yield raw_predictions.copy()

    def _compute_partial_dependence_recursion(self, grid, target_features):
        """Fast partial dependence computation.

        Parameters
        ----------
        grid : ndarray, shape (n_samples, n_target_features)
            The grid points on which the partial dependence should be
            evaluated.
        target_features : ndarray, shape (n_target_features)
            The set of target features for which the partial dependence
            should be evaluated.

        Returns
        -------
        averaged_predictions : ndarray, shape \
                (n_trees_per_iteration, n_samples)
            The value of the partial dependence function on each grid point.
        """

        if getattr(self, "_fitted_with_sw", False):
            raise NotImplementedError(
                "{} does not support partial dependence "
                "plots with the 'recursion' method when "
                "sample weights were given during fit "
                "time.".format(self.__class__.__name__)
            )

        grid = np.asarray(grid, dtype=X_DTYPE, order="C")
        averaged_predictions = np.zeros(
            (self.n_trees_per_iteration_, grid.shape[0]), dtype=Y_DTYPE
        )

        for predictors_of_ith_iteration in self._predictors:
            for k, predictor in enumerate(predictors_of_ith_iteration):
                predictor.compute_partial_dependence(
                    grid, target_features, averaged_predictions[k]
                )
        # Note that the learning rate is already accounted for in the leaves
        # values.

        return averaged_predictions

    def _more_tags(self):
        return {"allow_nan": True}

    @abstractmethod
    def _get_loss(self, sample_weight):
        pass

    @abstractmethod
    def _encode_y(self, y=None):
        pass

    @property
    def n_iter_(self):
        """Number of iterations of the boosting process."""
        check_is_fitted(self)
        return len(self._predictors)
