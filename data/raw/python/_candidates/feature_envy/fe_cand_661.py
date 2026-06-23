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

    K_gradient : ndarray of shape (n_samples_X, n_samples_X, n_dims)
        The gradient of the kernel k(X, X) with respect to the log of the
        hyperparameter of the kernel. Only returned when eval_gradient
        is True.
    """
    if len(np.atleast_1d(self.length_scale)) > 1:
        raise AttributeError(
            "RationalQuadratic kernel only supports isotropic version, "
            "please use a single scalar for length_scale"
        )
    X = np.atleast_2d(X)
    if Y is None:
        dists = squareform(pdist(X, metric="sqeuclidean"))
        tmp = dists / (2 * self.alpha * self.length_scale**2)
        base = 1 + tmp
        K = base**-self.alpha
        np.fill_diagonal(K, 1)
    else:
        if eval_gradient:
            raise ValueError("Gradient can only be evaluated when Y is None.")
        dists = cdist(X, Y, metric="sqeuclidean")
        K = (1 + dists / (2 * self.alpha * self.length_scale**2)) ** -self.alpha

    if eval_gradient:
        # gradient with respect to length_scale
        if not self.hyperparameter_length_scale.fixed:
            length_scale_gradient = dists * K / (self.length_scale**2 * base)
            length_scale_gradient = length_scale_gradient[:, :, np.newaxis]
        else:  # l is kept fixed
            length_scale_gradient = np.empty((K.shape[0], K.shape[1], 0))

        # gradient with respect to alpha
        if not self.hyperparameter_alpha.fixed:
            alpha_gradient = K * (
                -self.alpha * np.log(base)
                + dists / (2 * self.length_scale**2 * base)
            )
            alpha_gradient = alpha_gradient[:, :, np.newaxis]
        else:  # alpha is kept fixed
            alpha_gradient = np.empty((K.shape[0], K.shape[1], 0))

        return K, np.dstack((alpha_gradient, length_scale_gradient))
    else:
        return K
