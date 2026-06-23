def transform(self, X):
    """Apply dimensionality reduction to X.

    X is projected on the first principal components previously extracted
    from a training set, using minibatches of size batch_size if X is
    sparse.

    Parameters
    ----------
    X : {array-like, sparse matrix} of shape (n_samples, n_features)
        New data, where `n_samples` is the number of samples
        and `n_features` is the number of features.

    Returns
    -------
    X_new : ndarray of shape (n_samples, n_components)
        Projection of X in the first principal components.

    Examples
    --------

    >>> import numpy as np
    >>> from sklearn.decomposition import IncrementalPCA
    >>> X = np.array([[-1, -1], [-2, -1], [-3, -2],
    ...               [1, 1], [2, 1], [3, 2]])
    >>> ipca = IncrementalPCA(n_components=2, batch_size=3)
    >>> ipca.fit(X)
    IncrementalPCA(batch_size=3, n_components=2)
    >>> ipca.transform(X) # doctest: +SKIP
    """
    if sparse.issparse(X):
        n_samples = X.shape[0]
        output = []
        for batch in gen_batches(
            n_samples, self.batch_size_, min_batch_size=self.n_components or 0
        ):
            output.append(super().transform(X[batch].toarray()))
        return np.vstack(output)
    else:
        return super().transform(X)
