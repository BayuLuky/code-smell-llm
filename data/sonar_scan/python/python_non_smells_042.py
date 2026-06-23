def predict(self, X):
    """Estimate the best class label for each sample in X.

    This is implemented as ``argmax(decision_function(X), axis=1)`` which
    will return the label of the class with most votes by estimators
    predicting the outcome of a decision for each possible class pair.

    Parameters
    ----------
    X : {array-like, sparse matrix} of shape (n_samples, n_features)
        Data.

    Returns
    -------
    y : numpy array of shape [n_samples]
        Predicted multi-class targets.
    """
    Y = self.decision_function(X)
    if self.n_classes_ == 2:
        thresh = _threshold_for_binary_predict(self.estimators_[0])
        return self.classes_[(Y > thresh).astype(int)]
    return self.classes_[Y.argmax(axis=1)]
