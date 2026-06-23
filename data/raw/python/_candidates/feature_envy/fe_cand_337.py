def predict_proba(self, X):
    """Predict probability estimates.

    Parameters
    ----------
    X : {array-like, sparse matrix} of shape (n_samples, n_features)
        The input data.

    Returns
    -------
    Y_prob : array-like of shape (n_samples, n_classes)
        The predicted probabilities.
    """
    X = self._validate_data(X, accept_sparse=True, reset=False)
    Y_prob_chain = np.zeros((X.shape[0], len(self.estimators_)))
    Y_pred_chain = np.zeros((X.shape[0], len(self.estimators_)))
    for chain_idx, estimator in enumerate(self.estimators_):
        previous_predictions = Y_pred_chain[:, :chain_idx]
        if sp.issparse(X):
            X_aug = sp.hstack((X, previous_predictions))
        else:
            X_aug = np.hstack((X, previous_predictions))
        Y_prob_chain[:, chain_idx] = estimator.predict_proba(X_aug)[:, 1]
        Y_pred_chain[:, chain_idx] = estimator.predict(X_aug)
    inv_order = np.empty_like(self.order_)
    inv_order[self.order_] = np.arange(len(self.order_))
    Y_prob = Y_prob_chain[:, inv_order]

    return Y_prob
