def _run_answer_test(
    pos_input,
    pos_output,
    neighbors,
    grad_output,
    csr_container,
    verbose=False,
    perplexity=0.1,
    skip_num_points=0,
):
    distances = pairwise_distances(pos_input).astype(np.float32)
    args = distances, perplexity, verbose
    pos_output = pos_output.astype(np.float32)
    neighbors = neighbors.astype(np.int64, copy=False)
    pij_input = _joint_probabilities(*args)
    pij_input = squareform(pij_input).astype(np.float32)
    grad_bh = np.zeros(pos_output.shape, dtype=np.float32)

    P = csr_container(pij_input)

    neighbors = P.indices.astype(np.int64)
    indptr = P.indptr.astype(np.int64)

    _barnes_hut_tsne.gradient(
        P.data, pos_output, neighbors, indptr, grad_bh, 0.5, 2, 1, skip_num_points=0
    )
    assert_array_almost_equal(grad_bh, grad_output, decimal=4)
