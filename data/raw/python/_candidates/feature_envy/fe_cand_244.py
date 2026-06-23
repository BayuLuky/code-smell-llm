def _posterior_mode(self, K, return_temporaries=False):
    """Mode-finding for binary Laplace GPC and fixed kernel.

    This approximates the posterior of the latent function values for given
    inputs and target observations with a Gaussian approximation and uses
    Newton's iteration to find the mode of this approximation.
    """
    # Based on Algorithm 3.1 of GPML

    # If warm_start are enabled, we reuse the last solution for the
    # posterior mode as initialization; otherwise, we initialize with 0
    if (
        self.warm_start
        and hasattr(self, "f_cached")
        and self.f_cached.shape == self.y_train_.shape
    ):
        f = self.f_cached
    else:
        f = np.zeros_like(self.y_train_, dtype=np.float64)

    # Use Newton's iteration method to find mode of Laplace approximation
    log_marginal_likelihood = -np.inf
    for _ in range(self.max_iter_predict):
        # Line 4
        pi = expit(f)
        W = pi * (1 - pi)
        # Line 5
        W_sr = np.sqrt(W)
        W_sr_K = W_sr[:, np.newaxis] * K
        B = np.eye(W.shape[0]) + W_sr_K * W_sr
        L = cholesky(B, lower=True)
        # Line 6
        b = W * f + (self.y_train_ - pi)
        # Line 7
        a = b - W_sr * cho_solve((L, True), W_sr_K.dot(b))
        # Line 8
        f = K.dot(a)

        # Line 10: Compute log marginal likelihood in loop and use as
        #          convergence criterion
        lml = (
            -0.5 * a.T.dot(f)
            - np.log1p(np.exp(-(self.y_train_ * 2 - 1) * f)).sum()
            - np.log(np.diag(L)).sum()
        )
        # Check if we have converged (log marginal likelihood does
        # not decrease)
        # XXX: more complex convergence criterion
        if lml - log_marginal_likelihood < 1e-10:
            break
        log_marginal_likelihood = lml

    self.f_cached = f  # Remember solution for later warm-starts
    if return_temporaries:
        return log_marginal_likelihood, (pi, W_sr, L, b, a)
    else:
        return log_marginal_likelihood
