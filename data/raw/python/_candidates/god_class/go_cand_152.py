class BaseSGDRegressor(RegressorMixin, BaseSGD):
    loss_functions = {
        "squared_error": (SquaredLoss,),
        "huber": (Huber, DEFAULT_EPSILON),
        "epsilon_insensitive": (EpsilonInsensitive, DEFAULT_EPSILON),
        "squared_epsilon_insensitive": (SquaredEpsilonInsensitive, DEFAULT_EPSILON),
    }

    _parameter_constraints: dict = {
        **BaseSGD._parameter_constraints,
        "loss": [StrOptions(set(loss_functions))],
        "early_stopping": ["boolean"],
        "validation_fraction": [Interval(Real, 0, 1, closed="neither")],
        "n_iter_no_change": [Interval(Integral, 1, None, closed="left")],
    }

    @abstractmethod
    def __init__(
        self,
        loss="squared_error",
        *,
        penalty="l2",
        alpha=0.0001,
        l1_ratio=0.15,
        fit_intercept=True,
        max_iter=1000,
        tol=1e-3,
        shuffle=True,
        verbose=0,
        epsilon=DEFAULT_EPSILON,
        random_state=None,
        learning_rate="invscaling",
        eta0=0.01,
        power_t=0.25,
        early_stopping=False,
        validation_fraction=0.1,
        n_iter_no_change=5,
        warm_start=False,
        average=False,
    ):
        super().__init__(
            loss=loss,
            penalty=penalty,
            alpha=alpha,
            l1_ratio=l1_ratio,
            fit_intercept=fit_intercept,
            max_iter=max_iter,
            tol=tol,
            shuffle=shuffle,
            verbose=verbose,
            epsilon=epsilon,
            random_state=random_state,
            learning_rate=learning_rate,
            eta0=eta0,
            power_t=power_t,
            early_stopping=early_stopping,
            validation_fraction=validation_fraction,
            n_iter_no_change=n_iter_no_change,
            warm_start=warm_start,
            average=average,
        )

    def _partial_fit(
        self,
        X,
        y,
        alpha,
        C,
        loss,
        learning_rate,
        max_iter,
        sample_weight,
        coef_init,
        intercept_init,
    ):
        first_call = getattr(self, "coef_", None) is None
        X, y = self._validate_data(
            X,
            y,
            accept_sparse="csr",
            copy=False,
            order="C",
            dtype=[np.float64, np.float32],
            accept_large_sparse=False,
            reset=first_call,
        )
        y = y.astype(X.dtype, copy=False)

        n_samples, n_features = X.shape

        sample_weight = _check_sample_weight(sample_weight, X, dtype=X.dtype)

        # Allocate datastructures from input arguments
        if first_call:
            self._allocate_parameter_mem(
                n_classes=1,
                n_features=n_features,
                input_dtype=X.dtype,
                coef_init=coef_init,
                intercept_init=intercept_init,
            )
        if self.average > 0 and getattr(self, "_average_coef", None) is None:
            self._average_coef = np.zeros(n_features, dtype=X.dtype, order="C")
            self._average_intercept = np.zeros(1, dtype=X.dtype, order="C")

        self._fit_regressor(
            X, y, alpha, C, loss, learning_rate, sample_weight, max_iter
        )

        return self

    @_fit_context(prefer_skip_nested_validation=True)
    def partial_fit(self, X, y, sample_weight=None):
        """Perform one epoch of stochastic gradient descent on given samples.

        Internally, this method uses ``max_iter = 1``. Therefore, it is not
        guaranteed that a minimum of the cost function is reached after calling
        it once. Matters such as objective convergence and early stopping
        should be handled by the user.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape (n_samples, n_features)
            Subset of training data.

        y : numpy array of shape (n_samples,)
            Subset of target values.

        sample_weight : array-like, shape (n_samples,), default=None
            Weights applied to individual samples.
            If not provided, uniform weights are assumed.

        Returns
        -------
        self : object
            Returns an instance of self.
        """
        if not hasattr(self, "coef_"):
            self._more_validate_params(for_partial_fit=True)

        return self._partial_fit(
            X,
            y,
            self.alpha,
            C=1.0,
            loss=self.loss,
            learning_rate=self.learning_rate,
            max_iter=1,
            sample_weight=sample_weight,
            coef_init=None,
            intercept_init=None,
        )

    def _fit(
        self,
        X,
        y,
        alpha,
        C,
        loss,
        learning_rate,
        coef_init=None,
        intercept_init=None,
        sample_weight=None,
    ):
        if self.warm_start and getattr(self, "coef_", None) is not None:
            if coef_init is None:
                coef_init = self.coef_
            if intercept_init is None:
                intercept_init = self.intercept_
        else:
            self.coef_ = None
            self.intercept_ = None

        # Clear iteration count for multiple call to fit.
        self.t_ = 1.0

        self._partial_fit(
            X,
            y,
            alpha,
            C,
            loss,
            learning_rate,
            self.max_iter,
            sample_weight,
            coef_init,
            intercept_init,
        )

        if (
            self.tol is not None
            and self.tol > -np.inf
            and self.n_iter_ == self.max_iter
        ):
            warnings.warn(
                (
                    "Maximum number of iteration reached before "
                    "convergence. Consider increasing max_iter to "
                    "improve the fit."
                ),
                ConvergenceWarning,
            )

        return self

    @_fit_context(prefer_skip_nested_validation=True)
    def fit(self, X, y, coef_init=None, intercept_init=None, sample_weight=None):
        """Fit linear model with Stochastic Gradient Descent.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape (n_samples, n_features)
            Training data.

        y : ndarray of shape (n_samples,)
            Target values.

        coef_init : ndarray of shape (n_features,), default=None
            The initial coefficients to warm-start the optimization.

        intercept_init : ndarray of shape (1,), default=None
            The initial intercept to warm-start the optimization.

        sample_weight : array-like, shape (n_samples,), default=None
            Weights applied to individual samples (1. for unweighted).

        Returns
        -------
        self : object
            Fitted `SGDRegressor` estimator.
        """
        self._more_validate_params()

        return self._fit(
            X,
            y,
            alpha=self.alpha,
            C=1.0,
            loss=self.loss,
            learning_rate=self.learning_rate,
            coef_init=coef_init,
            intercept_init=intercept_init,
            sample_weight=sample_weight,
        )

    def _decision_function(self, X):
        """Predict using the linear model

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape (n_samples, n_features)

        Returns
        -------
        ndarray of shape (n_samples,)
           Predicted target values per element in X.
        """
        check_is_fitted(self)

        X = self._validate_data(X, accept_sparse="csr", reset=False)

        scores = safe_sparse_dot(X, self.coef_.T, dense_output=True) + self.intercept_
        return scores.ravel()

    def predict(self, X):
        """Predict using the linear model.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape (n_samples, n_features)
            Input data.

        Returns
        -------
        ndarray of shape (n_samples,)
           Predicted target values per element in X.
        """
        return self._decision_function(X)

    def _fit_regressor(
        self, X, y, alpha, C, loss, learning_rate, sample_weight, max_iter
    ):
        loss_function = self._get_loss_function(loss)
        penalty_type = self._get_penalty_type(self.penalty)
        learning_rate_type = self._get_learning_rate_type(learning_rate)

        if not hasattr(self, "t_"):
            self.t_ = 1.0

        validation_mask = self._make_validation_split(y, sample_mask=sample_weight > 0)
        validation_score_cb = self._make_validation_score_cb(
            validation_mask, X, y, sample_weight
        )

        random_state = check_random_state(self.random_state)
        # numpy mtrand expects a C long which is a signed 32 bit integer under
        # Windows
        seed = random_state.randint(0, MAX_INT)

        dataset, intercept_decay = make_dataset(
            X, y, sample_weight, random_state=random_state
        )

        tol = self.tol if self.tol is not None else -np.inf

        if self.average:
            coef = self._standard_coef
            intercept = self._standard_intercept
            average_coef = self._average_coef
            average_intercept = self._average_intercept
        else:
            coef = self.coef_
            intercept = self.intercept_
            average_coef = None  # Not used
            average_intercept = [0]  # Not used

        _plain_sgd = _get_plain_sgd_function(input_dtype=coef.dtype)
        coef, intercept, average_coef, average_intercept, self.n_iter_ = _plain_sgd(
            coef,
            intercept[0],
            average_coef,
            average_intercept[0],
            loss_function,
            penalty_type,
            alpha,
            C,
            self.l1_ratio,
            dataset,
            validation_mask,
            self.early_stopping,
            validation_score_cb,
            int(self.n_iter_no_change),
            max_iter,
            tol,
            int(self.fit_intercept),
            int(self.verbose),
            int(self.shuffle),
            seed,
            1.0,
            1.0,
            learning_rate_type,
            self.eta0,
            self.power_t,
            0,
            self.t_,
            intercept_decay,
            self.average,
        )

        self.t_ += self.n_iter_ * X.shape[0]

        if self.average > 0:
            self._average_intercept = np.atleast_1d(average_intercept)
            self._standard_intercept = np.atleast_1d(intercept)

            if self.average <= self.t_ - 1.0:
                # made enough updates for averaging to be taken into account
                self.coef_ = average_coef
                self.intercept_ = np.atleast_1d(average_intercept)
            else:
                self.coef_ = coef
                self.intercept_ = np.atleast_1d(intercept)

        else:
            self.intercept_ = np.atleast_1d(intercept)
