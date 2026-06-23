def fit(self, K, y=None):
    """Fit KernelCenterer.

    Parameters
    ----------
    K : ndarray of shape (n_samples, n_samples)
        Kernel matrix.

    y : None
        Ignored.

    Returns
    -------
    self : object
        Returns the instance itself.
    """
    xp, _ = get_namespace(K)

    K = self._validate_data(K, dtype=_array_api.supported_float_dtypes(xp))

    if K.shape[0] != K.shape[1]:
        raise ValueError(
            "Kernel matrix must be a square matrix."
            " Input is a {}x{} matrix.".format(K.shape[0], K.shape[1])
        )

    n_samples = K.shape[0]
    self.K_fit_rows_ = xp.sum(K, axis=0) / n_samples
    self.K_fit_all_ = xp.sum(self.K_fit_rows_) / n_samples
    return self
