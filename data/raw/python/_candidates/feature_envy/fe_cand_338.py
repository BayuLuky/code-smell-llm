def decision_function(self, X):
    """Evaluate the decision_function of the models in the chain.

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        The input data.

    Returns
    -------
    Y_decision : array-like of shape (n_samples, n_classes)
        Returns the decision function of the sample for each model
        in the chain.
    """
    X = self._validate_data(X, accept_sparse=True, reset=False)
    Y_decision_chain = np.zeros((X.shape[0], len(self.estimators_)))
    Y_pred_chain = np.zeros((X.shape[0], len(self.estimators_)))
    for chain_idx, estimator in enumerate(self.estimators_):
        previous_predictions = Y_pred_chain[:, :chain_idx]
        if sp.issparse(X):
            X_aug = sp.hstack((X, previous_predictions))
        else:
            X_aug = np.hstack((X, previous_predictions))
        Y_decision_chain[:, chain_idx] = estimator.decision_function(X_aug)
        Y_pred_chain[:, chain_idx] = estimator.predict(X_aug)

    inv_order = np.empty_like(self.order_)
    inv_order[self.order_] = np.arange(len(self.order_))
    Y_decision = Y_decision_chain[:, inv_order]

    return Y_decision
