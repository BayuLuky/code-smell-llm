def test_explicit_sparse_zeros(tree_type, csc_container, csr_container):
    TreeEstimator = ALL_TREES[tree_type]
    max_depth = 3
    n_features = 10

    # n_samples set n_feature to ease construction of a simultaneous
    # construction of a csr and csc matrix
    n_samples = n_features
    samples = np.arange(n_samples)

    # Generate X, y
    random_state = check_random_state(0)
    indices = []
    data = []
    offset = 0
    indptr = [offset]
    for i in range(n_features):
        n_nonzero_i = random_state.binomial(n_samples, 0.5)
        indices_i = random_state.permutation(samples)[:n_nonzero_i]
        indices.append(indices_i)
        data_i = random_state.binomial(3, 0.5, size=(n_nonzero_i,)) - 1
        data.append(data_i)
        offset += n_nonzero_i
        indptr.append(offset)

    indices = np.concatenate(indices).astype(np.int32)
    indptr = np.array(indptr, dtype=np.int32)
    data = np.array(np.concatenate(data), dtype=np.float32)
    X_sparse = csc_container((data, indices, indptr), shape=(n_samples, n_features))
    X = X_sparse.toarray()
    X_sparse_test = csr_container(
        (data, indices, indptr), shape=(n_samples, n_features)
    )
    X_test = X_sparse_test.toarray()
    y = random_state.randint(0, 3, size=(n_samples,))

    # Ensure that X_sparse_test owns its data, indices and indptr array
    X_sparse_test = X_sparse_test.copy()

    # Ensure that we have explicit zeros
    assert (X_sparse.data == 0.0).sum() > 0
    assert (X_sparse_test.data == 0.0).sum() > 0

    # Perform the comparison
    d = TreeEstimator(random_state=0, max_depth=max_depth).fit(X, y)
    s = TreeEstimator(random_state=0, max_depth=max_depth).fit(X_sparse, y)

    assert_tree_equal(
        d.tree_,
        s.tree_,
        "{0} with dense and sparse format gave different trees".format(tree),
    )

    Xs = (X_test, X_sparse_test)
    for X1, X2 in product(Xs, Xs):
        assert_array_almost_equal(s.tree_.apply(X1), d.tree_.apply(X2))
        assert_array_almost_equal(s.apply(X1), d.apply(X2))
        assert_array_almost_equal(s.apply(X1), s.tree_.apply(X1))

        assert_array_almost_equal(
            s.tree_.decision_path(X1).toarray(), d.tree_.decision_path(X2).toarray()
        )
        assert_array_almost_equal(
            s.decision_path(X1).toarray(), d.decision_path(X2).toarray()
        )
        assert_array_almost_equal(
            s.decision_path(X1).toarray(), s.tree_.decision_path(X1).toarray()
        )

        assert_array_almost_equal(s.predict(X1), d.predict(X2))

        if tree in CLF_TREES:
            assert_array_almost_equal(s.predict_proba(X1), d.predict_proba(X2))
