def transform(self, X, copy=True):
    """Transform a count matrix to a tf or tf-idf representation.

    Parameters
    ----------
    X : sparse matrix of (n_samples, n_features)
        A matrix of term/token counts.

    copy : bool, default=True
        Whether to copy X and operate on the copy or perform in-place
        operations.

    Returns
    -------
    vectors : sparse matrix of shape (n_samples, n_features)
        Tf-idf-weighted document-term matrix.
    """
    X = self._validate_data(
        X, accept_sparse="csr", dtype=FLOAT_DTYPES, copy=copy, reset=False
    )
    if not sp.issparse(X):
        X = sp.csr_matrix(X, dtype=np.float64)

    if self.sublinear_tf:
        np.log(X.data, X.data)
        X.data += 1

    if self.use_idf:
        # idf_ being a property, the automatic attributes detection
        # does not work as usual and we need to specify the attribute
        # name:
        check_is_fitted(self, attributes=["idf_"], msg="idf vector is not fitted")

        X = X @ self._idf_diag

    if self.norm is not None:
        X = normalize(X, norm=self.norm, copy=False)

    return X
