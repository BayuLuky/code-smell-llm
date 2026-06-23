def predict_proba(self, X):
    """Return posterior probabilities of classification.

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Array of samples/test vectors.

    Returns
    -------
    C : ndarray of shape (n_samples, n_classes)
        Posterior probabilities of classification per class.
    """
    values = self._decision_function(X)
    # compute the likelihood of the underlying gaussian models
    # up to a multiplicative constant.
    likelihood = np.exp(values - values.max(axis=1)[:, np.newaxis])
    # compute posterior probabilities
    return likelihood / likelihood.sum(axis=1)[:, np.newaxis]
