def fit(self, X, y):
    check_params = dict(
        force_all_finite=False, dtype=None, ensure_2d=False, accept_sparse=True
    )
    self._validate_data(
        X, y, reset=True, validate_separately=(check_params, check_params)
    )
    self.y_ = y
    return self
