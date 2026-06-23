def _get_gram(precompute, X, y):
    if (not hasattr(precompute, "__array__")) and (
        (precompute is True)
        or (precompute == "auto" and X.shape[0] > X.shape[1])
        or (precompute == "auto" and y.shape[1] > 1)
    ):
        precompute = np.dot(X.T, X)

    return precompute
