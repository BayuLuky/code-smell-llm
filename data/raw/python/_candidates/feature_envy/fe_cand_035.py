def inverse_transform(self, X):
    """Reverse the transformation operation.

    Parameters
    ----------
    X : array of shape [n_samples, n_selected_features]
        The input samples.

    Returns
    -------
    X_r : array of shape [n_samples, n_original_features]
        `X` with columns of zeros inserted where features would have
        been removed by :meth:`transform`.
    """
    if issparse(X):
        X = X.tocsc()
        # insert additional entries in indptr:
        # e.g. if transform changed indptr from [0 2 6 7] to [0 2 3]
        # col_nonzeros here will be [2 0 1] so indptr becomes [0 2 2 3]
        it = self.inverse_transform(np.diff(X.indptr).reshape(1, -1))
        col_nonzeros = it.ravel()
        indptr = np.concatenate([[0], np.cumsum(col_nonzeros)])
        Xt = csc_matrix(
            (X.data, X.indices, indptr),
            shape=(X.shape[0], len(indptr) - 1),
            dtype=X.dtype,
        )
        return Xt

    support = self.get_support()
    X = check_array(X, dtype=None)
    if support.sum() != X.shape[1]:
        raise ValueError("X has a different shape than during fitting.")

    if X.ndim == 1:
        X = X[None, :]
    Xt = np.zeros((X.shape[0], support.size), dtype=X.dtype)
    Xt[:, support] = X
    return Xt
