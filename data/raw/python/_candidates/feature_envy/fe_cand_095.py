def log_marginal_likelihood(
    self, theta=None, eval_gradient=False, clone_kernel=True
):
    """Returns log-marginal likelihood of theta for training data.

    Parameters
    ----------
    theta : array-like of shape (n_kernel_params,), default=None
        Kernel hyperparameters for which the log-marginal likelihood is
        evaluated. If None, the precomputed log_marginal_likelihood
        of ``self.kernel_.theta`` is returned.

    eval_gradient : bool, default=False
        If True, the gradient of the log-marginal likelihood with respect
        to the kernel hyperparameters at position theta is returned
        additionally. If True, theta must not be None.

    clone_kernel : bool, default=True
        If True, the kernel attribute is copied. If False, the kernel
        attribute is modified, but may result in a performance improvement.

    Returns
    -------
    log_likelihood : float
        Log-marginal likelihood of theta for training data.

    log_likelihood_gradient : ndarray of shape (n_kernel_params,), \
            optional
        Gradient of the log-marginal likelihood with respect to the kernel
        hyperparameters at position theta.
        Only returned when `eval_gradient` is True.
    """
    if theta is None:
        if eval_gradient:
            raise ValueError("Gradient can only be evaluated for theta!=None")
        return self.log_marginal_likelihood_value_

    if clone_kernel:
        kernel = self.kernel_.clone_with_theta(theta)
    else:
        kernel = self.kernel_
        kernel.theta = theta

    if eval_gradient:
        K, K_gradient = kernel(self.X_train_, eval_gradient=True)
    else:
        K = kernel(self.X_train_)

    # Compute log-marginal-likelihood Z and also store some temporaries
    # which can be reused for computing Z's gradient
    Z, (pi, W_sr, L, b, a) = self._posterior_mode(K, return_temporaries=True)

    if not eval_gradient:
        return Z

    # Compute gradient based on Algorithm 5.1 of GPML
    d_Z = np.empty(theta.shape[0])
    # XXX: Get rid of the np.diag() in the next line
    R = W_sr[:, np.newaxis] * cho_solve((L, True), np.diag(W_sr))  # Line 7
    C = solve(L, W_sr[:, np.newaxis] * K)  # Line 8
    # Line 9: (use einsum to compute np.diag(C.T.dot(C))))
    s_2 = (
        -0.5
        * (np.diag(K) - np.einsum("ij, ij -> j", C, C))
        * (pi * (1 - pi) * (1 - 2 * pi))
    )  # third derivative

    for j in range(d_Z.shape[0]):
        C = K_gradient[:, :, j]  # Line 11
        # Line 12: (R.T.ravel().dot(C.ravel()) = np.trace(R.dot(C)))
        s_1 = 0.5 * a.T.dot(C).dot(a) - 0.5 * R.T.ravel().dot(C.ravel())

        b = C.dot(self.y_train_ - pi)  # Line 13
        s_3 = b - K.dot(R.dot(b))  # Line 14

        d_Z[j] = s_1 + s_2.T.dot(s_3)  # Line 15

    return Z, d_Z
