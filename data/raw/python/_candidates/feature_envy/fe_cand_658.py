def _encode_y(self, y):
    # Just convert y to the expected dtype
    self.n_trees_per_iteration_ = 1
    y = y.astype(Y_DTYPE, copy=False)
    if self.loss == "gamma":
        # Ensure y > 0
        if not np.all(y > 0):
            raise ValueError("loss='gamma' requires strictly positive y.")
    elif self.loss == "poisson":
        # Ensure y >= 0 and sum(y) > 0
        if not (np.all(y >= 0) and np.sum(y) > 0):
            raise ValueError(
                "loss='poisson' requires non-negative y and sum(y) > 0."
            )
    return y
