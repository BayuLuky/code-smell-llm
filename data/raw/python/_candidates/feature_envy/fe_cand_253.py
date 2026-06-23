def predict(self, X):
    """Predict the target for the provided data.

    Parameters
    ----------
    X : {array-like, sparse matrix} of shape (n_queries, n_features), \
            or (n_queries, n_indexed) if metric == 'precomputed'
        Test samples.

    Returns
    -------
    y : ndarray of shape (n_queries,) or (n_queries, n_outputs), dtype=int
        Target values.
    """
    if self.weights == "uniform":
        # In that case, we do not need the distances to perform
        # the weighting so we do not compute them.
        neigh_ind = self.kneighbors(X, return_distance=False)
        neigh_dist = None
    else:
        neigh_dist, neigh_ind = self.kneighbors(X)

    weights = _get_weights(neigh_dist, self.weights)

    _y = self._y
    if _y.ndim == 1:
        _y = _y.reshape((-1, 1))

    if weights is None:
        y_pred = np.mean(_y[neigh_ind], axis=1)
    else:
        y_pred = np.empty((neigh_dist.shape[0], _y.shape[1]), dtype=np.float64)
        denom = np.sum(weights, axis=1)

        for j in range(_y.shape[1]):
            num = np.sum(_y[neigh_ind, j] * weights, axis=1)
            y_pred[:, j] = num / denom

    if self._y.ndim == 1:
        y_pred = y_pred.ravel()

    return y_pred
