def fit(self, X, y=None):
    """Learn the idf vector (global term weights).

    Parameters
    ----------
    X : sparse matrix of shape (n_samples, n_features)
        A matrix of term/token counts.

    y : None
        This parameter is not needed to compute tf-idf.

    Returns
    -------
    self : object
        Fitted transformer.
    """
    # large sparse data is not supported for 32bit platforms because
    # _document_frequency uses np.bincount which works on arrays of
    # dtype NPY_INTP which is int32 for 32bit platforms. See #20923
    X = self._validate_data(
        X, accept_sparse=("csr", "csc"), accept_large_sparse=not _IS_32BIT
    )
    if not sp.issparse(X):
        X = sp.csr_matrix(X)
    dtype = X.dtype if X.dtype in FLOAT_DTYPES else np.float64

    if self.use_idf:
        n_samples, n_features = X.shape
        df = _document_frequency(X)
        df = df.astype(dtype, copy=False)

        # perform idf smoothing if required
        df += int(self.smooth_idf)
        n_samples += int(self.smooth_idf)

        # log+1 instead of log makes sure terms with zero idf don't get
        # suppressed entirely.
        idf = np.log(n_samples / df) + 1
        self._idf_diag = sp.diags(
            idf,
            offsets=0,
            shape=(n_features, n_features),
            format="csr",
            dtype=dtype,
        )

    return self
