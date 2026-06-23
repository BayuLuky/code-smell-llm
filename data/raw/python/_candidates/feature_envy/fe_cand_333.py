def _log_marginal_likelihood(
    self, n_samples, n_features, eigen_vals, alpha_, lambda_, coef, rmse
):
    """Log marginal likelihood."""
    alpha_1 = self.alpha_1
    alpha_2 = self.alpha_2
    lambda_1 = self.lambda_1
    lambda_2 = self.lambda_2

    # compute the log of the determinant of the posterior covariance.
    # posterior covariance is given by
    # sigma = (lambda_ * np.eye(n_features) + alpha_ * np.dot(X.T, X))^-1
    if n_samples > n_features:
        logdet_sigma = -np.sum(np.log(lambda_ + alpha_ * eigen_vals))
    else:
        logdet_sigma = np.full(n_features, lambda_, dtype=np.array(lambda_).dtype)
        logdet_sigma[:n_samples] += alpha_ * eigen_vals
        logdet_sigma = -np.sum(np.log(logdet_sigma))

    score = lambda_1 * log(lambda_) - lambda_2 * lambda_
    score += alpha_1 * log(alpha_) - alpha_2 * alpha_
    score += 0.5 * (
        n_features * log(lambda_)
        + n_samples * log(alpha_)
        - alpha_ * rmse
        - lambda_ * np.sum(coef**2)
        + logdet_sigma
        - n_samples * log(2 * np.pi)
    )

    return score
