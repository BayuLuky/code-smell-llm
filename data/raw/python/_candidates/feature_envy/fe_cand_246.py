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

    K_gradient : ndarray of shape (n_samples_X, n_samples_X, n_dims),\
            optional
        The gradient of the kernel k(X, X) with respect to the log of the
        hyperparameter of the kernel. Only returned when `eval_gradient`
        is True.
    """
    X = np.atleast_2d(X)
    if Y is None:
        K = np.inner(X, X) + self.sigma_0**2
    else:
        if eval_gradient:
            raise ValueError("Gradient can only be evaluated when Y is None.")
        K = np.inner(X, Y) + self.sigma_0**2

    if eval_gradient:
        if not self.hyperparameter_sigma_0.fixed:
            K_gradient = np.empty((K.shape[0], K.shape[1], 1))
            K_gradient[..., 0] = 2 * self.sigma_0**2
            return K, K_gradient
        else:
            return K, np.empty((X.shape[0], X.shape[0], 0))
    else:
        return K
