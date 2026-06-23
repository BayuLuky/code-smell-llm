def idf_(self, value):
    value = np.asarray(value, dtype=np.float64)
    n_features = value.shape[0]
    self._idf_diag = sp.spdiags(
        value, diags=0, m=n_features, n=n_features, format="csr"
    )
