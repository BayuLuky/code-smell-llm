def test_min_max(
    dtype,
    axis,
    sparse_format,
    missing_values,
    min_func,
    max_func,
    ignore_nan,
    large_indices,
):
    X = np.array(
        [
            [0, 3, 0],
            [2, -1, missing_values],
            [0, 0, 0],
            [9, missing_values, 7],
            [4, 0, 5],
        ],
        dtype=dtype,
    )
    X_sparse = sparse_format(X)

    if large_indices:
        X_sparse.indices = X_sparse.indices.astype("int64")
        X_sparse.indptr = X_sparse.indptr.astype("int64")

    mins_sparse, maxs_sparse = min_max_axis(X_sparse, axis=axis, ignore_nan=ignore_nan)
    assert_array_equal(mins_sparse, min_func(X, axis=axis))
    assert_array_equal(maxs_sparse, max_func(X, axis=axis))
