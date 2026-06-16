def __call__(self, X, Y=None, eval_gradient=False):
    """Return the kernel k(X, Y) and optionally its gradient.

    Parameters
    ----------
    X : ndarray of shape (n_samples_X, n_features)
        Left argument of the returned kernel k(X, Y)

    Y : ndarray of shape (n_samples_Y, n_features), default=None
        Right argument of the returned kernel k(X, Y). If None, k(X, X)
        if evaluated instead.

    eval_gradient : bool, default=False
        Determines whether the gradient with respect to the log of
        the kernel hyperparameter is computed.
        Only supported when Y is None.

    Returns
    -------
    K : ndarray of shape (n_samples_X, n_samples_Y)
        Kernel k(X, Y)

    K_gradient : ndarray of shape (n_samples_X, n_samples_X, n_dims), \
            optional
        The gradient of the kernel k(X, X) with respect to the log of the
        hyperparameter of the kernel. Only returned when `eval_gradient`
        is True.
    """
    X = np.atleast_2d(X)
    if Y is None:
        dists = squareform(pdist(X, metric="euclidean"))
        arg = np.pi * dists / self.periodicity
        sin_of_arg = np.sin(arg)
        K = np.exp(-2 * (sin_of_arg / self.length_scale) ** 2)
    else:
        if eval_gradient:
            raise ValueError("Gradient can only be evaluated when Y is None.")
        dists = cdist(X, Y, metric="euclidean")
        K = np.exp(
            -2 * (np.sin(np.pi / self.periodicity * dists) / self.length_scale) ** 2
        )

    if eval_gradient:
        cos_of_arg = np.cos(arg)
        # gradient with respect to length_scale
        if not self.hyperparameter_length_scale.fixed:
            length_scale_gradient = 4 / self.length_scale**2 * sin_of_arg**2 * K
            length_scale_gradient = length_scale_gradient[:, :, np.newaxis]
        else:  # length_scale is kept fixed
            length_scale_gradient = np.empty((K.shape[0], K.shape[1], 0))
        # gradient with respect to p
        if not self.hyperparameter_periodicity.fixed:
            periodicity_gradient = (
                4 * arg / self.length_scale**2 * cos_of_arg * sin_of_arg * K
            )
            periodicity_gradient = periodicity_gradient[:, :, np.newaxis]
        else:  # p is kept fixed
            periodicity_gradient = np.empty((K.shape[0], K.shape[1], 0))

        return K, np.dstack((length_scale_gradient, periodicity_gradient))
    else:
        return K
