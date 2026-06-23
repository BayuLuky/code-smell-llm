def score(self, X, y):
    """Return the mean accuracy on the given test data and labels.

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Test samples.

    y : array-like of shape (n_samples, n_outputs)
        True values for X.

    Returns
    -------
    scores : float
        Mean accuracy of predicted target versus true target.
    """
    check_is_fitted(self)
    n_outputs_ = len(self.estimators_)
    if y.ndim == 1:
        raise ValueError(
            "y must have at least two dimensions for "
            "multi target classification but has only one"
        )
    if y.shape[1] != n_outputs_:
        raise ValueError(
            "The number of outputs of Y for fit {0} and"
            " score {1} should be same".format(n_outputs_, y.shape[1])
        )
    y_pred = self.predict(X)
    return np.mean(np.all(y == y_pred, axis=1))
