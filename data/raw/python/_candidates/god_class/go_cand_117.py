class PowerTransformer(OneToOneFeatureMixin, TransformerMixin, BaseEstimator):
    """Apply a power transform featurewise to make data more Gaussian-like.

    Power transforms are a family of parametric, monotonic transformations
    that are applied to make data more Gaussian-like. This is useful for
    modeling issues related to heteroscedasticity (non-constant variance),
    or other situations where normality is desired.

    Currently, PowerTransformer supports the Box-Cox transform and the
    Yeo-Johnson transform. The optimal parameter for stabilizing variance and
    minimizing skewness is estimated through maximum likelihood.

    Box-Cox requires input data to be strictly positive, while Yeo-Johnson
    supports both positive or negative data.

    By default, zero-mean, unit-variance normalization is applied to the
    transformed data.

    For an example visualization, refer to :ref:`Compare PowerTransformer with
    other scalers <plot_all_scaling_power_transformer_section>`. To see the
    effect of Box-Cox and Yeo-Johnson transformations on different
    distributions, see:
    :ref:`sphx_glr_auto_examples_preprocessing_plot_map_data_to_normal.py`.

    Read more in the :ref:`User Guide <preprocessing_transformer>`.

    .. versionadded:: 0.20

    Parameters
    ----------
    method : {'yeo-johnson', 'box-cox'}, default='yeo-johnson'
        The power transform method. Available methods are:

        - 'yeo-johnson' [1]_, works with positive and negative values
        - 'box-cox' [2]_, only works with strictly positive values

    standardize : bool, default=True
        Set to True to apply zero-mean, unit-variance normalization to the
        transformed output.

    copy : bool, default=True
        Set to False to perform inplace computation during transformation.

    Attributes
    ----------
    lambdas_ : ndarray of float of shape (n_features,)
        The parameters of the power transformation for the selected features.

    n_features_in_ : int
        Number of features seen during :term:`fit`.

        .. versionadded:: 0.24

    feature_names_in_ : ndarray of shape (`n_features_in_`,)
        Names of features seen during :term:`fit`. Defined only when `X`
        has feature names that are all strings.

        .. versionadded:: 1.0

    See Also
    --------
    power_transform : Equivalent function without the estimator API.

    QuantileTransformer : Maps data to a standard normal distribution with
        the parameter `output_distribution='normal'`.

    Notes
    -----
    NaNs are treated as missing values: disregarded in ``fit``, and maintained
    in ``transform``.

    References
    ----------

    .. [1] :doi:`I.K. Yeo and R.A. Johnson, "A new family of power
           transformations to improve normality or symmetry." Biometrika,
           87(4), pp.954-959, (2000). <10.1093/biomet/87.4.954>`

    .. [2] :doi:`G.E.P. Box and D.R. Cox, "An Analysis of Transformations",
           Journal of the Royal Statistical Society B, 26, 211-252 (1964).
           <10.1111/j.2517-6161.1964.tb00553.x>`

    Examples
    --------
    >>> import numpy as np
    >>> from sklearn.preprocessing import PowerTransformer
    >>> pt = PowerTransformer()
    >>> data = [[1, 2], [3, 2], [4, 5]]
    >>> print(pt.fit(data))
    PowerTransformer()
    >>> print(pt.lambdas_)
    [ 1.386... -3.100...]
    >>> print(pt.transform(data))
    [[-1.316... -0.707...]
     [ 0.209... -0.707...]
     [ 1.106...  1.414...]]
    """

    _parameter_constraints: dict = {
        "method": [StrOptions({"yeo-johnson", "box-cox"})],
        "standardize": ["boolean"],
        "copy": ["boolean"],
    }

    def __init__(self, method="yeo-johnson", *, standardize=True, copy=True):
        self.method = method
        self.standardize = standardize
        self.copy = copy

    @_fit_context(prefer_skip_nested_validation=True)
    def fit(self, X, y=None):
        """Estimate the optimal parameter lambda for each feature.

        The optimal lambda parameter for minimizing skewness is estimated on
        each feature independently using maximum likelihood.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The data used to estimate the optimal transformation parameters.

        y : None
            Ignored.

        Returns
        -------
        self : object
            Fitted transformer.
        """
        self._fit(X, y=y, force_transform=False)
        return self

    @_fit_context(prefer_skip_nested_validation=True)
    def fit_transform(self, X, y=None):
        """Fit `PowerTransformer` to `X`, then transform `X`.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The data used to estimate the optimal transformation parameters
            and to be transformed using a power transformation.

        y : Ignored
            Not used, present for API consistency by convention.

        Returns
        -------
        X_new : ndarray of shape (n_samples, n_features)
            Transformed data.
        """
        return self._fit(X, y, force_transform=True)

    def _fit(self, X, y=None, force_transform=False):
        X = self._check_input(X, in_fit=True, check_positive=True)

        if not self.copy and not force_transform:  # if call from fit()
            X = X.copy()  # force copy so that fit does not change X inplace

        n_samples = X.shape[0]
        mean = np.mean(X, axis=0, dtype=np.float64)
        var = np.var(X, axis=0, dtype=np.float64)

        optim_function = {
            "box-cox": self._box_cox_optimize,
            "yeo-johnson": self._yeo_johnson_optimize,
        }[self.method]

        transform_function = {
            "box-cox": boxcox,
            "yeo-johnson": self._yeo_johnson_transform,
        }[self.method]

        with np.errstate(invalid="ignore"):  # hide NaN warnings
            self.lambdas_ = np.empty(X.shape[1], dtype=X.dtype)
            for i, col in enumerate(X.T):
                # For yeo-johnson, leave constant features unchanged
                # lambda=1 corresponds to the identity transformation
                is_constant_feature = _is_constant_feature(var[i], mean[i], n_samples)
                if self.method == "yeo-johnson" and is_constant_feature:
                    self.lambdas_[i] = 1.0
                    continue

                self.lambdas_[i] = optim_function(col)

                if self.standardize or force_transform:
                    X[:, i] = transform_function(X[:, i], self.lambdas_[i])

        if self.standardize:
            self._scaler = StandardScaler(copy=False).set_output(transform="default")
            if force_transform:
                X = self._scaler.fit_transform(X)
            else:
                self._scaler.fit(X)

        return X

    def transform(self, X):
        """Apply the power transform to each feature using the fitted lambdas.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The data to be transformed using a power transformation.

        Returns
        -------
        X_trans : ndarray of shape (n_samples, n_features)
            The transformed data.
        """
        check_is_fitted(self)
        X = self._check_input(X, in_fit=False, check_positive=True, check_shape=True)

        transform_function = {
            "box-cox": boxcox,
            "yeo-johnson": self._yeo_johnson_transform,
        }[self.method]
        for i, lmbda in enumerate(self.lambdas_):
            with np.errstate(invalid="ignore"):  # hide NaN warnings
                X[:, i] = transform_function(X[:, i], lmbda)

        if self.standardize:
            X = self._scaler.transform(X)

        return X

    def inverse_transform(self, X):
        """Apply the inverse power transformation using the fitted lambdas.

        The inverse of the Box-Cox transformation is given by::

            if lambda_ == 0:
                X = exp(X_trans)
            else:
                X = (X_trans * lambda_ + 1) ** (1 / lambda_)

        The inverse of the Yeo-Johnson transformation is given by::

            if X >= 0 and lambda_ == 0:
                X = exp(X_trans) - 1
            elif X >= 0 and lambda_ != 0:
                X = (X_trans * lambda_ + 1) ** (1 / lambda_) - 1
            elif X < 0 and lambda_ != 2:
                X = 1 - (-(2 - lambda_) * X_trans + 1) ** (1 / (2 - lambda_))
            elif X < 0 and lambda_ == 2:
                X = 1 - exp(-X_trans)

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The transformed data.

        Returns
        -------
        X : ndarray of shape (n_samples, n_features)
            The original data.
        """
        check_is_fitted(self)
        X = self._check_input(X, in_fit=False, check_shape=True)

        if self.standardize:
            X = self._scaler.inverse_transform(X)

        inv_fun = {
            "box-cox": self._box_cox_inverse_tranform,
            "yeo-johnson": self._yeo_johnson_inverse_transform,
        }[self.method]
        for i, lmbda in enumerate(self.lambdas_):
            with np.errstate(invalid="ignore"):  # hide NaN warnings
                X[:, i] = inv_fun(X[:, i], lmbda)

        return X

    def _box_cox_inverse_tranform(self, x, lmbda):
        """Return inverse-transformed input x following Box-Cox inverse
        transform with parameter lambda.
        """
        if lmbda == 0:
            x_inv = np.exp(x)
        else:
            x_inv = (x * lmbda + 1) ** (1 / lmbda)

        return x_inv

    def _yeo_johnson_inverse_transform(self, x, lmbda):
        """Return inverse-transformed input x following Yeo-Johnson inverse
        transform with parameter lambda.
        """
        x_inv = np.zeros_like(x)
        pos = x >= 0

        # when x >= 0
        if abs(lmbda) < np.spacing(1.0):
            x_inv[pos] = np.exp(x[pos]) - 1
        else:  # lmbda != 0
            x_inv[pos] = np.power(x[pos] * lmbda + 1, 1 / lmbda) - 1

        # when x < 0
        if abs(lmbda - 2) > np.spacing(1.0):
            x_inv[~pos] = 1 - np.power(-(2 - lmbda) * x[~pos] + 1, 1 / (2 - lmbda))
        else:  # lmbda == 2
            x_inv[~pos] = 1 - np.exp(-x[~pos])

        return x_inv

    def _yeo_johnson_transform(self, x, lmbda):
        """Return transformed input x following Yeo-Johnson transform with
        parameter lambda.
        """

        out = np.zeros_like(x)
        pos = x >= 0  # binary mask

        # when x >= 0
        if abs(lmbda) < np.spacing(1.0):
            out[pos] = np.log1p(x[pos])
        else:  # lmbda != 0
            out[pos] = (np.power(x[pos] + 1, lmbda) - 1) / lmbda

        # when x < 0
        if abs(lmbda - 2) > np.spacing(1.0):
            out[~pos] = -(np.power(-x[~pos] + 1, 2 - lmbda) - 1) / (2 - lmbda)
        else:  # lmbda == 2
            out[~pos] = -np.log1p(-x[~pos])

        return out

    def _box_cox_optimize(self, x):
        """Find and return optimal lambda parameter of the Box-Cox transform by
        MLE, for observed data x.

        We here use scipy builtins which uses the brent optimizer.
        """
        mask = np.isnan(x)
        if np.all(mask):
            raise ValueError("Column must not be all nan.")

        # the computation of lambda is influenced by NaNs so we need to
        # get rid of them
        _, lmbda = stats.boxcox(x[~mask], lmbda=None)

        return lmbda

    def _yeo_johnson_optimize(self, x):
        """Find and return optimal lambda parameter of the Yeo-Johnson
        transform by MLE, for observed data x.

        Like for Box-Cox, MLE is done via the brent optimizer.
        """
        x_tiny = np.finfo(np.float64).tiny

        def _neg_log_likelihood(lmbda):
            """Return the negative log likelihood of the observed data x as a
            function of lambda."""
            x_trans = self._yeo_johnson_transform(x, lmbda)
            n_samples = x.shape[0]
            x_trans_var = x_trans.var()

            # Reject transformed data that would raise a RuntimeWarning in np.log
            if x_trans_var < x_tiny:
                return np.inf

            log_var = np.log(x_trans_var)
            loglike = -n_samples / 2 * log_var
            loglike += (lmbda - 1) * (np.sign(x) * np.log1p(np.abs(x))).sum()

            return -loglike

        # the computation of lambda is influenced by NaNs so we need to
        # get rid of them
        x = x[~np.isnan(x)]
        # choosing bracket -2, 2 like for boxcox
        return optimize.brent(_neg_log_likelihood, brack=(-2, 2))

    def _check_input(self, X, in_fit, check_positive=False, check_shape=False):
        """Validate the input before fit and transform.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)

        in_fit : bool
            Whether or not `_check_input` is called from `fit` or other
            methods, e.g. `predict`, `transform`, etc.

        check_positive : bool, default=False
            If True, check that all data is positive and non-zero (only if
            ``self.method=='box-cox'``).

        check_shape : bool, default=False
            If True, check that n_features matches the length of self.lambdas_
        """
        X = self._validate_data(
            X,
            ensure_2d=True,
            dtype=FLOAT_DTYPES,
            copy=self.copy,
            force_all_finite="allow-nan",
            reset=in_fit,
        )

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", r"All-NaN (slice|axis) encountered")
            if check_positive and self.method == "box-cox" and np.nanmin(X) <= 0:
                raise ValueError(
                    "The Box-Cox transformation can only be "
                    "applied to strictly positive data"
                )

        if check_shape and not X.shape[1] == len(self.lambdas_):
            raise ValueError(
                "Input data has a different number of features "
                "than fitting data. Should have {n}, data has {m}".format(
                    n=len(self.lambdas_), m=X.shape[1]
                )
            )

        return X

    def _more_tags(self):
        return {"allow_nan": True}
