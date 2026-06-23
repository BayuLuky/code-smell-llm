def fit(self, X, y, sample_weight=None):
    """Fit Ridge regression model.

    Parameters
    ----------
    X : {ndarray, sparse matrix} of shape (n_samples, n_features)
        Training data.

    y : ndarray of shape (n_samples,) or (n_samples, n_targets)
        Target values.

    sample_weight : float or ndarray of shape (n_samples,), default=None
        Individual weights for each sample. If given a float, every sample
        will have the same weight.

    Returns
    -------
    self : object
        Fitted estimator.
    """
    _accept_sparse = _get_valid_accept_sparse(sparse.issparse(X), self.solver)
    X, y = self._validate_data(
        X,
        y,
        accept_sparse=_accept_sparse,
        dtype=[np.float64, np.float32],
        multi_output=True,
        y_numeric=True,
    )
    return super().fit(X, y, sample_weight=sample_weight)
