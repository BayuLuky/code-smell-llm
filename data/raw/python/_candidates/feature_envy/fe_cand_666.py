def inverse_transform(self, Xt):
    """
    Transform discretized data back to original feature space.

    Note that this function does not regenerate the original data
    due to discretization rounding.

    Parameters
    ----------
    Xt : array-like of shape (n_samples, n_features)
        Transformed data in the binned space.

    Returns
    -------
    Xinv : ndarray, dtype={np.float32, np.float64}
        Data in the original feature space.
    """
    check_is_fitted(self)

    if "onehot" in self.encode:
        Xt = self._encoder.inverse_transform(Xt)

    Xinv = check_array(Xt, copy=True, dtype=(np.float64, np.float32))
    n_features = self.n_bins_.shape[0]
    if Xinv.shape[1] != n_features:
        raise ValueError(
            "Incorrect number of features. Expecting {}, received {}.".format(
                n_features, Xinv.shape[1]
            )
        )

    for jj in range(n_features):
        bin_edges = self.bin_edges_[jj]
        bin_centers = (bin_edges[1:] + bin_edges[:-1]) * 0.5
        Xinv[:, jj] = bin_centers[(Xinv[:, jj]).astype(np.int64)]

    return Xinv
