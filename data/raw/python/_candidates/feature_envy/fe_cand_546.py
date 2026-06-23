def __call__(self, X, Y=None, eval_gradient=False):
    """Return the kernel k(X, Y) and optionally its gradient.

    Parameters
    ----------
    X : array-like of shape (n_samples_X, n_features) or list of object
        Left argument of the returned kernel k(X, Y)

    Y : array-like of shape (n_samples_X, n_features) or list of object,\
        default=None
        Right argument of the returned kernel k(X, Y). If None, k(X, X)
        is evaluated instead.

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
        hyperparameter of the kernel. Only returned when eval_gradient
        is True.
    """
    if Y is not None and eval_gradient:
        raise ValueError("Gradient can only be evaluated when Y is None.")

    if Y is None:
        K = self.noise_level * np.eye(_num_samples(X))
        if eval_gradient:
            if not self.hyperparameter_noise_level.fixed:
                return (
                    K,
                    self.noise_level * np.eye(_num_samples(X))[:, :, np.newaxis],
                )
            else:
                return K, np.empty((_num_samples(X), _num_samples(X), 0))
        else:
            return K
    else:
        return np.zeros((_num_samples(X), _num_samples(Y)))
