def transform(self, X):
    """Transform data to polynomial features.

    Parameters
    ----------
    X : {array-like, sparse matrix} of shape (n_samples, n_features)
        The data to transform, row by row.

        Prefer CSR over CSC for sparse input (for speed), but CSC is
        required if the degree is 4 or higher. If the degree is less than
        4 and the input format is CSC, it will be converted to CSR, have
        its polynomial features generated, then converted back to CSC.

        If the degree is 2 or 3, the method described in "Leveraging
        Sparsity to Speed Up Polynomial Feature Expansions of CSR Matrices
        Using K-Simplex Numbers" by Andrew Nystrom and John Hughes is
        used, which is much faster than the method used on CSC input. For
        this reason, a CSC input will be converted to CSR, and the output
        will be converted back to CSC prior to being returned, hence the
        preference of CSR.

    Returns
    -------
    XP : {ndarray, sparse matrix} of shape (n_samples, NP)
        The matrix of features, where `NP` is the number of polynomial
        features generated from the combination of inputs. If a sparse
        matrix is provided, it will be converted into a sparse
        `csr_matrix`.
    """
    check_is_fitted(self)

    X = self._validate_data(
        X, order="F", dtype=FLOAT_DTYPES, reset=False, accept_sparse=("csr", "csc")
    )

    n_samples, n_features = X.shape
    max_int32 = np.iinfo(np.int32).max
    if sparse.issparse(X) and X.format == "csr":
        if self._max_degree > 3:
            return self.transform(X.tocsc()).tocsr()
        to_stack = []
        if self.include_bias:
            to_stack.append(
                sparse.csr_matrix(np.ones(shape=(n_samples, 1), dtype=X.dtype))
            )
        if self._min_degree <= 1 and self._max_degree > 0:
            to_stack.append(X)

        cumulative_size = sum(mat.shape[1] for mat in to_stack)
        for deg in range(max(2, self._min_degree), self._max_degree + 1):
            expanded = _create_expansion(
                X=X,
                interaction_only=self.interaction_only,
                deg=deg,
                n_features=n_features,
                cumulative_size=cumulative_size,
            )
            if expanded is not None:
                to_stack.append(expanded)
                cumulative_size += expanded.shape[1]
        if len(to_stack) == 0:
            # edge case: deal with empty matrix
            XP = sparse.csr_matrix((n_samples, 0), dtype=X.dtype)
        else:
            # `scipy.sparse.hstack` breaks in scipy<1.9.2
            # when `n_output_features_ > max_int32`
            all_int32 = all(mat.indices.dtype == np.int32 for mat in to_stack)
            if (
                sp_version < parse_version("1.9.2")
                and self.n_output_features_ > max_int32
                and all_int32
            ):
                raise ValueError(  # pragma: no cover
                    "In scipy versions `<1.9.2`, the function `scipy.sparse.hstack`"
                    " produces negative columns when:\n1. The output shape contains"
                    " `n_cols` too large to be represented by a 32bit signed"
                    " integer.\n2. All sub-matrices to be stacked have indices of"
                    " dtype `np.int32`.\nTo avoid this error, either use a version"
                    " of scipy `>=1.9.2` or alter the `PolynomialFeatures`"
                    " transformer to produce fewer than 2^31 output features"
                )
            XP = sparse.hstack(to_stack, dtype=X.dtype, format="csr")
    elif sparse.issparse(X) and X.format == "csc" and self._max_degree < 4:
        return self.transform(X.tocsr()).tocsc()
    elif sparse.issparse(X):
        combinations = self._combinations(
            n_features=n_features,
            min_degree=self._min_degree,
            max_degree=self._max_degree,
            interaction_only=self.interaction_only,
            include_bias=self.include_bias,
        )
        columns = []
        for combi in combinations:
            if combi:
                out_col = 1
                for col_idx in combi:
                    out_col = X[:, [col_idx]].multiply(out_col)
                columns.append(out_col)
            else:
                bias = sparse.csc_matrix(np.ones((X.shape[0], 1)))
                columns.append(bias)
        XP = sparse.hstack(columns, dtype=X.dtype).tocsc()
    else:
        # Do as if _min_degree = 0 and cut down array after the
        # computation, i.e. use _n_out_full instead of n_output_features_.
        XP = np.empty(
            shape=(n_samples, self._n_out_full), dtype=X.dtype, order=self.order
        )

        # What follows is a faster implementation of:
        # for i, comb in enumerate(combinations):
        #     XP[:, i] = X[:, comb].prod(1)
        # This implementation uses two optimisations.
        # First one is broadcasting,
        # multiply ([X1, ..., Xn], X1) -> [X1 X1, ..., Xn X1]
        # multiply ([X2, ..., Xn], X2) -> [X2 X2, ..., Xn X2]
        # ...
        # multiply ([X[:, start:end], X[:, start]) -> ...
        # Second optimisation happens for degrees >= 3.
        # Xi^3 is computed reusing previous computation:
        # Xi^3 = Xi^2 * Xi.

        # degree 0 term
        if self.include_bias:
            XP[:, 0] = 1
            current_col = 1
        else:
            current_col = 0

        if self._max_degree == 0:
            return XP

        # degree 1 term
        XP[:, current_col : current_col + n_features] = X
        index = list(range(current_col, current_col + n_features))
        current_col += n_features
        index.append(current_col)

        # loop over degree >= 2 terms
        for _ in range(2, self._max_degree + 1):
            new_index = []
            end = index[-1]
            for feature_idx in range(n_features):
                start = index[feature_idx]
                new_index.append(current_col)
                if self.interaction_only:
                    start += index[feature_idx + 1] - index[feature_idx]
                next_col = current_col + end - start
                if next_col <= current_col:
                    break
                # XP[:, start:end] are terms of degree d - 1
                # that exclude feature #feature_idx.
                np.multiply(
                    XP[:, start:end],
                    X[:, feature_idx : feature_idx + 1],
                    out=XP[:, current_col:next_col],
                    casting="no",
                )
                current_col = next_col

            new_index.append(current_col)
            index = new_index

        if self._min_degree > 1:
            n_XP, n_Xout = self._n_out_full, self.n_output_features_
            if self.include_bias:
                Xout = np.empty(
                    shape=(n_samples, n_Xout), dtype=XP.dtype, order=self.order
                )
                Xout[:, 0] = 1
                Xout[:, 1:] = XP[:, n_XP - n_Xout + 1 :]
            else:
                Xout = XP[:, n_XP - n_Xout :].copy()
            XP = Xout
    return XP
