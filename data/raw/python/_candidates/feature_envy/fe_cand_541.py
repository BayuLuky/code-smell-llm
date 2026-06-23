def _svd(self, array, n_components, n_discard):
    """Returns first `n_components` left and right singular
    vectors u and v, discarding the first `n_discard`.
    """
    if self.svd_method == "randomized":
        kwargs = {}
        if self.n_svd_vecs is not None:
            kwargs["n_oversamples"] = self.n_svd_vecs
        u, _, vt = randomized_svd(
            array, n_components, random_state=self.random_state, **kwargs
        )

    elif self.svd_method == "arpack":
        u, _, vt = svds(array, k=n_components, ncv=self.n_svd_vecs)
        if np.any(np.isnan(vt)):
            # some eigenvalues of A * A.T are negative, causing
            # sqrt() to be np.nan. This causes some vectors in vt
            # to be np.nan.
            A = safe_sparse_dot(array.T, array)
            random_state = check_random_state(self.random_state)
            # initialize with [-1,1] as in ARPACK
            v0 = random_state.uniform(-1, 1, A.shape[0])
            _, v = eigsh(A, ncv=self.n_svd_vecs, v0=v0)
            vt = v.T
        if np.any(np.isnan(u)):
            A = safe_sparse_dot(array, array.T)
            random_state = check_random_state(self.random_state)
            # initialize with [-1,1] as in ARPACK
            v0 = random_state.uniform(-1, 1, A.shape[0])
            _, u = eigsh(A, ncv=self.n_svd_vecs, v0=v0)

    assert_all_finite(u)
    assert_all_finite(vt)
    u = u[:, n_discard:]
    vt = vt[n_discard:]
    return u, vt.T
