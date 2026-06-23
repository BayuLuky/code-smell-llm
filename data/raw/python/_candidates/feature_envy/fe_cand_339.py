def partial_fit(self, X, y=None):
    """Online computation of max absolute value of X for later scaling.

    All of X is processed as a single batch. This is intended for cases
    when :meth:`fit` is not feasible due to very large number of
    `n_samples` or because X is read from a continuous stream.

    Parameters
    ----------
    X : {array-like, sparse matrix} of shape (n_samples, n_features)
        The data used to compute the mean and standard deviation
        used for later scaling along the features axis.

    y : None
        Ignored.

    Returns
    -------
    self : object
        Fitted scaler.
    """
    xp, _ = get_namespace(X)

    first_pass = not hasattr(self, "n_samples_seen_")
    X = self._validate_data(
        X,
        reset=first_pass,
        accept_sparse=("csr", "csc"),
        dtype=_array_api.supported_float_dtypes(xp),
        force_all_finite="allow-nan",
    )

    if sparse.issparse(X):
        mins, maxs = min_max_axis(X, axis=0, ignore_nan=True)
        max_abs = np.maximum(np.abs(mins), np.abs(maxs))
    else:
        max_abs = _array_api._nanmax(xp.abs(X), axis=0)

    if first_pass:
        self.n_samples_seen_ = X.shape[0]
    else:
        max_abs = xp.maximum(self.max_abs_, max_abs)
        self.n_samples_seen_ += X.shape[0]

    self.max_abs_ = max_abs
    self.scale_ = _handle_zeros_in_scale(max_abs, copy=True)
    return self
