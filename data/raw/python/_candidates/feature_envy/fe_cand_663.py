def transform(self, X):
    """Transform X.

    This is implemented by linking the points X into the graph of geodesic
    distances of the training data. First the `n_neighbors` nearest
    neighbors of X are found in the training data, and from these the
    shortest geodesic distances from each point in X to each point in
    the training data are computed in order to construct the kernel.
    The embedding of X is the projection of this kernel onto the
    embedding vectors of the training set.

    Parameters
    ----------
    X : {array-like, sparse matrix}, shape (n_queries, n_features)
        If neighbors_algorithm='precomputed', X is assumed to be a
        distance matrix or a sparse graph of shape
        (n_queries, n_samples_fit).

    Returns
    -------
    X_new : array-like, shape (n_queries, n_components)
        X transformed in the new space.
    """
    check_is_fitted(self)
    if self.n_neighbors is not None:
        distances, indices = self.nbrs_.kneighbors(X, return_distance=True)
    else:
        distances, indices = self.nbrs_.radius_neighbors(X, return_distance=True)

    # Create the graph of shortest distances from X to
    # training data via the nearest neighbors of X.
    # This can be done as a single array operation, but it potentially
    # takes a lot of memory.  To avoid that, use a loop:

    n_samples_fit = self.nbrs_.n_samples_fit_
    n_queries = distances.shape[0]

    if hasattr(X, "dtype") and X.dtype == np.float32:
        dtype = np.float32
    else:
        dtype = np.float64

    G_X = np.zeros((n_queries, n_samples_fit), dtype)
    for i in range(n_queries):
        G_X[i] = np.min(self.dist_matrix_[indices[i]] + distances[i][:, None], 0)

    G_X **= 2
    G_X *= -0.5

    return self.kernel_pca_.transform(G_X)
