def pairwise_distances_argmin_min(
    X, Y, *, axis=1, metric="euclidean", metric_kwargs=None
):
    """Compute minimum distances between one point and a set of points.

    This function computes for each row in X, the index of the row of Y which
    is closest (according to the specified distance). The minimal distances are
    also returned.

    This is mostly equivalent to calling:

        (pairwise_distances(X, Y=Y, metric=metric).argmin(axis=axis),
         pairwise_distances(X, Y=Y, metric=metric).min(axis=axis))

    but uses much less memory, and is faster for large arrays.

    Parameters
    ----------
    X : {array-like, sparse matrix} of shape (n_samples_X, n_features)
        Array containing points.

    Y : {array-like, sparse matrix} of shape (n_samples_Y, n_features)
        Array containing points.

    axis : int, default=1
        Axis along which the argmin and distances are to be computed.

    metric : str or callable, default='euclidean'
        Metric to use for distance computation. Any metric from scikit-learn
        or scipy.spatial.distance can be used.

        If metric is a callable function, it is called on each
        pair of instances (rows) and the resulting value recorded. The callable
        should take two arrays as input and return one value indicating the
        distance between them. This works for Scipy's metrics, but is less
        efficient than passing the metric name as a string.

        Distance matrices are not supported.

        Valid values for metric are:

        - from scikit-learn: ['cityblock', 'cosine', 'euclidean', 'l1', 'l2',
          'manhattan']

        - from scipy.spatial.distance: ['braycurtis', 'canberra', 'chebyshev',
          'correlation', 'dice', 'hamming', 'jaccard', 'kulsinski',
          'mahalanobis', 'minkowski', 'rogerstanimoto', 'russellrao',
          'seuclidean', 'sokalmichener', 'sokalsneath', 'sqeuclidean',
          'yule']

        See the documentation for scipy.spatial.distance for details on these
        metrics.

        .. note::
           `'kulsinski'` is deprecated from SciPy 1.9 and will be removed in SciPy 1.11.

        .. note::
           `'matching'` has been removed in SciPy 1.9 (use `'hamming'` instead).

    metric_kwargs : dict, default=None
        Keyword arguments to pass to specified metric function.

    Returns
    -------
    argmin : ndarray
        Y[argmin[i], :] is the row in Y that is closest to X[i, :].

    distances : ndarray
        The array of minimum distances. `distances[i]` is the distance between
        the i-th row in X and the argmin[i]-th row in Y.

    See Also
    --------
    pairwise_distances : Distances between every pair of samples of X and Y.
    pairwise_distances_argmin : Same as `pairwise_distances_argmin_min` but only
        returns the argmins.

    Examples
    --------
    >>> from sklearn.metrics.pairwise import pairwise_distances_argmin_min
    >>> X = [[0, 0, 0], [1, 1, 1]]
    >>> Y = [[1, 0, 0], [1, 1, 0]]
    >>> argmin, distances = pairwise_distances_argmin_min(X, Y)
    >>> argmin
    array([0, 1])
    >>> distances
    array([1., 1.])
    """
    X, Y = check_pairwise_arrays(X, Y)

    if axis == 0:
        X, Y = Y, X

    if metric_kwargs is None:
        metric_kwargs = {}

    if ArgKmin.is_usable_for(X, Y, metric):
        # This is an adaptor for one "sqeuclidean" specification.
        # For this backend, we can directly use "sqeuclidean".
        if metric_kwargs.get("squared", False) and metric == "euclidean":
            metric = "sqeuclidean"
            metric_kwargs = {}

        values, indices = ArgKmin.compute(
            X=X,
            Y=Y,
            k=1,
            metric=metric,
            metric_kwargs=metric_kwargs,
            strategy="auto",
            return_distance=True,
        )
        values = values.flatten()
        indices = indices.flatten()
    else:
        # Joblib-based backend, which is used when user-defined callable
        # are passed for metric.

        # This won't be used in the future once PairwiseDistancesReductions support:
        #   - DistanceMetrics which work on supposedly binary data
        #   - CSR-dense and dense-CSR case if 'euclidean' in metric.

        # Turn off check for finiteness because this is costly and because arrays
        # have already been validated.
        with config_context(assume_finite=True):
            indices, values = zip(
                *pairwise_distances_chunked(
                    X, Y, reduce_func=_argmin_min_reduce, metric=metric, **metric_kwargs
                )
            )
        indices = np.concatenate(indices)
        values = np.concatenate(values)

    return indices, values
