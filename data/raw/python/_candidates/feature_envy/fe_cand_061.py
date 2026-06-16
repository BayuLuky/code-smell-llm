def _update_sigma_woodbury(self, X, alpha_, lambda_, keep_lambda):
    # See slides as referenced in the docstring note
    # this function is used when n_samples < n_features and will invert
    # a matrix of shape (n_samples, n_samples) making use of the
    # woodbury formula:
    # https://en.wikipedia.org/wiki/Woodbury_matrix_identity
    n_samples = X.shape[0]
    X_keep = X[:, keep_lambda]
    inv_lambda = 1 / lambda_[keep_lambda].reshape(1, -1)
    sigma_ = pinvh(
        np.eye(n_samples, dtype=X.dtype) / alpha_
        + np.dot(X_keep * inv_lambda, X_keep.T)
    )
    sigma_ = np.dot(sigma_, X_keep * inv_lambda)
    sigma_ = -np.dot(inv_lambda.reshape(-1, 1) * X_keep.T, sigma_)
    sigma_[np.diag_indices(sigma_.shape[1])] += 1.0 / lambda_[keep_lambda]
    return sigma_
