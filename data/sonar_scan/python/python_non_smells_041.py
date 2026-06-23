def decision_function(self, X):
    """Decision function for the OneVsRestClassifier.

    Return the distance of each sample from the decision boundary for each
    class. This can only be used with estimators which implement the
    `decision_function` method.

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Input data.

    Returns
    -------
    T : array-like of shape (n_samples, n_classes) or (n_samples,) for \
        binary classification.
        Result of calling `decision_function` on the final estimator.

        .. versionchanged:: 0.19
            output shape changed to ``(n_samples,)`` to conform to
            scikit-learn conventions for binary classification.
    """
    check_is_fitted(self)
    if len(self.estimators_) == 1:
        return self.estimators_[0].decision_function(X)
    return np.array(
        [est.decision_function(X).ravel() for est in self.estimators_]
    ).T
