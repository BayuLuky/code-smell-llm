def transform(self, X):
    """Transform each feature data to B-splines.

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        The data to transform.

    Returns
    -------
    XBS : {ndarray, sparse matrix} of shape (n_samples, n_features * n_splines)
        The matrix of features, where n_splines is the number of bases
        elements of the B-splines, n_knots + degree - 1.
    """
    check_is_fitted(self)

    X = self._validate_data(X, reset=False, accept_sparse=False, ensure_2d=True)

    n_samples, n_features = X.shape
    n_splines = self.bsplines_[0].c.shape[1]
    degree = self.degree

    # TODO: Remove this condition, once scipy 1.10 is the minimum version.
    #       Only scipy => 1.10 supports design_matrix(.., extrapolate=..).
    #       The default (implicit in scipy < 1.10) is extrapolate=False.
    scipy_1_10 = sp_version >= parse_version("1.10.0")
    # Note: self.bsplines_[0].extrapolate is True for extrapolation in
    # ["periodic", "continue"]
    if scipy_1_10:
        use_sparse = self.sparse_output
        kwargs_extrapolate = {"extrapolate": self.bsplines_[0].extrapolate}
    else:
        use_sparse = self.sparse_output and not self.bsplines_[0].extrapolate
        kwargs_extrapolate = dict()

    # Note that scipy BSpline returns float64 arrays and converts input
    # x=X[:, i] to c-contiguous float64.
    n_out = self.n_features_out_ + n_features * (1 - self.include_bias)
    if X.dtype in FLOAT_DTYPES:
        dtype = X.dtype
    else:
        dtype = np.float64
    if use_sparse:
        output_list = []
    else:
        XBS = np.zeros((n_samples, n_out), dtype=dtype, order=self.order)

    for i in range(n_features):
        spl = self.bsplines_[i]

        if self.extrapolation in ("continue", "error", "periodic"):
            if self.extrapolation == "periodic":
                # With periodic extrapolation we map x to the segment
                # [spl.t[k], spl.t[n]].
                # This is equivalent to BSpline(.., extrapolate="periodic")
                # for scipy>=1.0.0.
                n = spl.t.size - spl.k - 1
                # Assign to new array to avoid inplace operation
                x = spl.t[spl.k] + (X[:, i] - spl.t[spl.k]) % (
                    spl.t[n] - spl.t[spl.k]
                )
            else:
                x = X[:, i]

            if use_sparse:
                XBS_sparse = BSpline.design_matrix(
                    x, spl.t, spl.k, **kwargs_extrapolate
                )
                if self.extrapolation == "periodic":
                    # See the construction of coef in fit. We need to add the last
                    # degree spline basis function to the first degree ones and
                    # then drop the last ones.
                    # Note: See comment about SparseEfficiencyWarning below.
                    XBS_sparse = XBS_sparse.tolil()
                    XBS_sparse[:, :degree] += XBS_sparse[:, -degree:]
                    XBS_sparse = XBS_sparse[:, :-degree]
            else:
                XBS[:, (i * n_splines) : ((i + 1) * n_splines)] = spl(x)
        else:  # extrapolation in ("constant", "linear")
            xmin, xmax = spl.t[degree], spl.t[-degree - 1]
            # spline values at boundaries
            f_min, f_max = spl(xmin), spl(xmax)
            mask = (xmin <= X[:, i]) & (X[:, i] <= xmax)
            if use_sparse:
                mask_inv = ~mask
                x = X[:, i].copy()
                # Set some arbitrary values outside boundary that will be reassigned
                # later.
                x[mask_inv] = spl.t[self.degree]
                XBS_sparse = BSpline.design_matrix(x, spl.t, spl.k)
                # Note: Without converting to lil_matrix we would get:
                # scipy.sparse._base.SparseEfficiencyWarning: Changing the sparsity
                # structure of a csr_matrix is expensive. lil_matrix is more
                # efficient.
                if np.any(mask_inv):
                    XBS_sparse = XBS_sparse.tolil()
                    XBS_sparse[mask_inv, :] = 0
            else:
                XBS[mask, (i * n_splines) : ((i + 1) * n_splines)] = spl(X[mask, i])

        # Note for extrapolation:
        # 'continue' is already returned as is by scipy BSplines
        if self.extrapolation == "error":
            # BSpline with extrapolate=False does not raise an error, but
            # outputs np.nan.
            if (use_sparse and np.any(np.isnan(XBS_sparse.data))) or (
                not use_sparse
                and np.any(
                    np.isnan(XBS[:, (i * n_splines) : ((i + 1) * n_splines)])
                )
            ):
                raise ValueError(
                    "X contains values beyond the limits of the knots."
                )
        elif self.extrapolation == "constant":
            # Set all values beyond xmin and xmax to the value of the
            # spline basis functions at those two positions.
            # Only the first degree and last degree number of splines
            # have non-zero values at the boundaries.

            mask = X[:, i] < xmin
            if np.any(mask):
                if use_sparse:
                    # Note: See comment about SparseEfficiencyWarning above.
                    XBS_sparse = XBS_sparse.tolil()
                    XBS_sparse[mask, :degree] = f_min[:degree]

                else:
                    XBS[mask, (i * n_splines) : (i * n_splines + degree)] = f_min[
                        :degree
                    ]

            mask = X[:, i] > xmax
            if np.any(mask):
                if use_sparse:
                    # Note: See comment about SparseEfficiencyWarning above.
                    XBS_sparse = XBS_sparse.tolil()
                    XBS_sparse[mask, -degree:] = f_max[-degree:]
                else:
                    XBS[
                        mask,
                        ((i + 1) * n_splines - degree) : ((i + 1) * n_splines),
                    ] = f_max[-degree:]

        elif self.extrapolation == "linear":
            # Continue the degree first and degree last spline bases
            # linearly beyond the boundaries, with slope = derivative at
            # the boundary.
            # Note that all others have derivative = value = 0 at the
            # boundaries.

            # spline derivatives = slopes at boundaries
            fp_min, fp_max = spl(xmin, nu=1), spl(xmax, nu=1)
            # Compute the linear continuation.
            if degree <= 1:
                # For degree=1, the derivative of 2nd spline is not zero at
                # boundary. For degree=0 it is the same as 'constant'.
                degree += 1
            for j in range(degree):
                mask = X[:, i] < xmin
                if np.any(mask):
                    linear_extr = f_min[j] + (X[mask, i] - xmin) * fp_min[j]
                    if use_sparse:
                        # Note: See comment about SparseEfficiencyWarning above.
                        XBS_sparse = XBS_sparse.tolil()
                        XBS_sparse[mask, j] = linear_extr
                    else:
                        XBS[mask, i * n_splines + j] = linear_extr

                mask = X[:, i] > xmax
                if np.any(mask):
                    k = n_splines - 1 - j
                    linear_extr = f_max[k] + (X[mask, i] - xmax) * fp_max[k]
                    if use_sparse:
                        # Note: See comment about SparseEfficiencyWarning above.
                        XBS_sparse = XBS_sparse.tolil()
                        XBS_sparse[mask, k : k + 1] = linear_extr[:, None]
                    else:
                        XBS[mask, i * n_splines + k] = linear_extr

        if use_sparse:
            XBS_sparse = XBS_sparse.tocsr()
            output_list.append(XBS_sparse)

    if use_sparse:
        # TODO: Remove this conditional error when the minimum supported version of
        # SciPy is 1.9.2
        # `scipy.sparse.hstack` breaks in scipy<1.9.2
        # when `n_features_out_ > max_int32`
        max_int32 = np.iinfo(np.int32).max
        all_int32 = True
        for mat in output_list:
            all_int32 &= mat.indices.dtype == np.int32
        if (
            sp_version < parse_version("1.9.2")
            and self.n_features_out_ > max_int32
            and all_int32
        ):
            raise ValueError(
                "In scipy versions `<1.9.2`, the function `scipy.sparse.hstack`"
                " produces negative columns when:\n1. The output shape contains"
                " `n_cols` too large to be represented by a 32bit signed"
                " integer.\n. All sub-matrices to be stacked have indices of"
                " dtype `np.int32`.\nTo avoid this error, either use a version"
                " of scipy `>=1.9.2` or alter the `SplineTransformer`"
                " transformer to produce fewer than 2^31 output features"
            )
        XBS = sparse.hstack(output_list, format="csr")
    elif self.sparse_output:
        # TODO: Remove ones scipy 1.10 is the minimum version. See comments above.
        XBS = sparse.csr_matrix(XBS)

    if self.include_bias:
        return XBS
    else:
        # We throw away one spline basis per feature.
        # We chose the last one.
        indices = [j for j in range(XBS.shape[1]) if (j + 1) % n_splines != 0]
        return XBS[:, indices]
