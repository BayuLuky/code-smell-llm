def test_incr_mean_variance_axis_weighted_axis0(
    Xw, X, weights, sparse_constructor, dtype
):
    axis = 0
    Xw_sparse = sparse_constructor(Xw).astype(dtype)
    X_sparse = sparse_constructor(X).astype(dtype)

    last_mean = np.zeros(np.size(Xw, 1), dtype=dtype)
    last_var = np.zeros_like(last_mean)
    last_n = np.zeros_like(last_mean, dtype=np.int64)
    means0, vars0, n_incr0 = incr_mean_variance_axis(
        X=X_sparse,
        axis=axis,
        last_mean=last_mean,
        last_var=last_var,
        last_n=last_n,
        weights=None,
    )

    means_w0, vars_w0, n_incr_w0 = incr_mean_variance_axis(
        X=Xw_sparse,
        axis=axis,
        last_mean=last_mean,
        last_var=last_var,
        last_n=last_n,
        weights=weights,
    )

    assert means_w0.dtype == dtype
    assert vars_w0.dtype == dtype
    assert n_incr_w0.dtype == dtype

    means_simple, vars_simple = mean_variance_axis(X=X_sparse, axis=axis)

    assert_array_almost_equal(means0, means_w0)
    assert_array_almost_equal(means0, means_simple)
    assert_array_almost_equal(vars0, vars_w0)
    assert_array_almost_equal(vars0, vars_simple)
    assert_array_almost_equal(n_incr0, n_incr_w0)

    # check second round for incremental
    means1, vars1, n_incr1 = incr_mean_variance_axis(
        X=X_sparse,
        axis=axis,
        last_mean=means0,
        last_var=vars0,
        last_n=n_incr0,
        weights=None,
    )

    means_w1, vars_w1, n_incr_w1 = incr_mean_variance_axis(
        X=Xw_sparse,
        axis=axis,
        last_mean=means_w0,
        last_var=vars_w0,
        last_n=n_incr_w0,
        weights=weights,
    )

    assert_array_almost_equal(means1, means_w1)
    assert_array_almost_equal(vars1, vars_w1)
    assert_array_almost_equal(n_incr1, n_incr_w1)

    assert means_w1.dtype == dtype
    assert vars_w1.dtype == dtype
    assert n_incr_w1.dtype == dtype
