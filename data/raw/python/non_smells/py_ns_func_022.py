def predict(self, X):
    check_is_fitted(self)
    self._validate_data(
        X,
        force_all_finite=False,
        dtype=None,
        accept_sparse=True,
        ensure_2d=False,
        reset=False,
    )

    return np.repeat(self.y_, _num_samples(X))
