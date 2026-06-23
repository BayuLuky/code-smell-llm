def _update_sigma(self, X, alpha_, lambda_, keep_lambda):
    # See slides as referenced in the docstring note
    # this function is used when n_samples >= n_features and will
    # invert a matrix of shape (n_features, n_features)
    X_keep = X[:, keep_lambda]
    gram = np.dot(X_keep.T, X_keep)
    eye = np.eye(gram.shape[0], dtype=X.dtype)
    sigma_inv = lambda_[keep_lambda] * eye + alpha_ * gram
    sigma_ = pinvh(sigma_inv)
    return sigma_
