def predict_proba(self, X):
    check_is_fitted(self)
    self._validate_data(
        X,
        force_all_finite=False,
        dtype=None,
        accept_sparse=True,
        ensure_2d=False,
        reset=False,
    )
    y_ = self.y_.astype(np.float64)
    return np.repeat([np.hstack([1 - y_, y_])], _num_samples(X), axis=0)
