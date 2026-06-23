def predict(self, X):
    """Predict on the data matrix X using the ClassifierChain model.

    Parameters
    ----------
    X : {array-like, sparse matrix} of shape (n_samples, n_features)
        The input data.

    Returns
    -------
    Y_pred : array-like of shape (n_samples, n_classes)
        The predicted values.
    """
    check_is_fitted(self)
    X = self._validate_data(X, accept_sparse=True, reset=False)
    Y_pred_chain = np.zeros((X.shape[0], len(self.estimators_)))
    for chain_idx, estimator in enumerate(self.estimators_):
        previous_predictions = Y_pred_chain[:, :chain_idx]
        if sp.issparse(X):
            if chain_idx == 0:
                X_aug = X
            else:
                X_aug = sp.hstack((X, previous_predictions))
        else:
            X_aug = np.hstack((X, previous_predictions))
        Y_pred_chain[:, chain_idx] = estimator.predict(X_aug)

    inv_order = np.empty_like(self.order_)
    inv_order[self.order_] = np.arange(len(self.order_))
    Y_pred = Y_pred_chain[:, inv_order]

    return Y_pred
