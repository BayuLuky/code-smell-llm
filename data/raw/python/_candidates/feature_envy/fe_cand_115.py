def _update_coef_(
    self, X, y, n_samples, n_features, XT_y, U, Vh, eigen_vals_, alpha_, lambda_
):
    """Update posterior mean and compute corresponding rmse.

    Posterior mean is given by coef_ = scaled_sigma_ * X.T * y where
    scaled_sigma_ = (lambda_/alpha_ * np.eye(n_features)
                     + np.dot(X.T, X))^-1
    """

    if n_samples > n_features:
        coef_ = np.linalg.multi_dot(
            [Vh.T, Vh / (eigen_vals_ + lambda_ / alpha_)[:, np.newaxis], XT_y]
        )
    else:
        coef_ = np.linalg.multi_dot(
            [X.T, U / (eigen_vals_ + lambda_ / alpha_)[None, :], U.T, y]
        )

    rmse_ = np.sum((y - np.dot(X, coef_)) ** 2)

    return coef_, rmse_
