def _validate_input(self, X, y, incremental, reset):
    X, y = self._validate_data(
        X,
        y,
        accept_sparse=["csr", "csc"],
        multi_output=True,
        y_numeric=True,
        dtype=(np.float64, np.float32),
        reset=reset,
    )
    if y.ndim == 2 and y.shape[1] == 1:
        y = column_or_1d(y, warn=True)
    return X, y
