def test_min_impurity_decrease(global_random_seed):
    # test if min_impurity_decrease ensure that a split is made only if
    # if the impurity decrease is at least that value
    X, y = datasets.make_classification(n_samples=100, random_state=global_random_seed)

    # test both DepthFirstTreeBuilder and BestFirstTreeBuilder
    # by setting max_leaf_nodes
    for max_leaf_nodes, name in product((None, 1000), ALL_TREES.keys()):
        TreeEstimator = ALL_TREES[name]

        # Check default value of min_impurity_decrease, 1e-7
        est1 = TreeEstimator(max_leaf_nodes=max_leaf_nodes, random_state=0)
        # Check with explicit value of 0.05
        est2 = TreeEstimator(
            max_leaf_nodes=max_leaf_nodes, min_impurity_decrease=0.05, random_state=0
        )
        # Check with a much lower value of 0.0001
        est3 = TreeEstimator(
            max_leaf_nodes=max_leaf_nodes, min_impurity_decrease=0.0001, random_state=0
        )
        # Check with a much lower value of 0.1
        est4 = TreeEstimator(
            max_leaf_nodes=max_leaf_nodes, min_impurity_decrease=0.1, random_state=0
        )

        for est, expected_decrease in (
            (est1, 1e-7),
            (est2, 0.05),
            (est3, 0.0001),
            (est4, 0.1),
        ):
            assert (
                est.min_impurity_decrease <= expected_decrease
            ), "Failed, min_impurity_decrease = {0} > {1}".format(
                est.min_impurity_decrease, expected_decrease
            )
            est.fit(X, y)
            for node in range(est.tree_.node_count):
                # If current node is a not leaf node, check if the split was
                # justified w.r.t the min_impurity_decrease
                if est.tree_.children_left[node] != TREE_LEAF:
                    imp_parent = est.tree_.impurity[node]
                    wtd_n_node = est.tree_.weighted_n_node_samples[node]

                    left = est.tree_.children_left[node]
                    wtd_n_left = est.tree_.weighted_n_node_samples[left]
                    imp_left = est.tree_.impurity[left]
                    wtd_imp_left = wtd_n_left * imp_left

                    right = est.tree_.children_right[node]
                    wtd_n_right = est.tree_.weighted_n_node_samples[right]
                    imp_right = est.tree_.impurity[right]
                    wtd_imp_right = wtd_n_right * imp_right

                    wtd_avg_left_right_imp = wtd_imp_right + wtd_imp_left
                    wtd_avg_left_right_imp /= wtd_n_node

                    fractional_node_weight = (
                        est.tree_.weighted_n_node_samples[node] / X.shape[0]
                    )

                    actual_decrease = fractional_node_weight * (
                        imp_parent - wtd_avg_left_right_imp
                    )

                    assert (
                        actual_decrease >= expected_decrease
                    ), "Failed with {0} expected min_impurity_decrease={1}".format(
                        actual_decrease, expected_decrease
                    )
