def test_mae():
    """Check MAE criterion produces correct results on small toy dataset:

    ------------------
    | X | y | weight |
    ------------------
    | 3 | 3 |  0.1   |
    | 5 | 3 |  0.3   |
    | 8 | 4 |  1.0   |
    | 3 | 6 |  0.6   |
    | 5 | 7 |  0.3   |
    ------------------
    |sum wt:|  2.3   |
    ------------------

    Because we are dealing with sample weights, we cannot find the median by
    simply choosing/averaging the centre value(s), instead we consider the
    median where 50% of the cumulative weight is found (in a y sorted data set)
    . Therefore with regards to this test data, the cumulative weight is >= 50%
    when y = 4.  Therefore:
    Median = 4

    For all the samples, we can get the total error by summing:
    Absolute(Median - y) * weight

    I.e., total error = (Absolute(4 - 3) * 0.1)
                      + (Absolute(4 - 3) * 0.3)
                      + (Absolute(4 - 4) * 1.0)
                      + (Absolute(4 - 6) * 0.6)
                      + (Absolute(4 - 7) * 0.3)
                      = 2.5

    Impurity = Total error / total weight
             = 2.5 / 2.3
             = 1.08695652173913
             ------------------

    From this root node, the next best split is between X values of 3 and 5.
    Thus, we have left and right child nodes:

    LEFT                    RIGHT
    ------------------      ------------------
    | X | y | weight |      | X | y | weight |
    ------------------      ------------------
    | 3 | 3 |  0.1   |      | 5 | 3 |  0.3   |
    | 3 | 6 |  0.6   |      | 8 | 4 |  1.0   |
    ------------------      | 5 | 7 |  0.3   |
    |sum wt:|  0.7   |      ------------------
    ------------------      |sum wt:|  1.6   |
                            ------------------

    Impurity is found in the same way:
    Left node Median = 6
    Total error = (Absolute(6 - 3) * 0.1)
                + (Absolute(6 - 6) * 0.6)
                = 0.3

    Left Impurity = Total error / total weight
            = 0.3 / 0.7
            = 0.428571428571429
            -------------------

    Likewise for Right node:
    Right node Median = 4
    Total error = (Absolute(4 - 3) * 0.3)
                + (Absolute(4 - 4) * 1.0)
                + (Absolute(4 - 7) * 0.3)
                = 1.2

    Right Impurity = Total error / total weight
            = 1.2 / 1.6
            = 0.75
            ------
    """
    dt_mae = DecisionTreeRegressor(
        random_state=0, criterion="absolute_error", max_leaf_nodes=2
    )

    # Test MAE where sample weights are non-uniform (as illustrated above):
    dt_mae.fit(
        X=[[3], [5], [3], [8], [5]],
        y=[6, 7, 3, 4, 3],
        sample_weight=[0.6, 0.3, 0.1, 1.0, 0.3],
    )
    assert_allclose(dt_mae.tree_.impurity, [2.5 / 2.3, 0.3 / 0.7, 1.2 / 1.6])
    assert_array_equal(dt_mae.tree_.value.flat, [4.0, 6.0, 4.0])

    # Test MAE where all sample weights are uniform:
    dt_mae.fit(X=[[3], [5], [3], [8], [5]], y=[6, 7, 3, 4, 3], sample_weight=np.ones(5))
    assert_array_equal(dt_mae.tree_.impurity, [1.4, 1.5, 4.0 / 3.0])
    assert_array_equal(dt_mae.tree_.value.flat, [4, 4.5, 4.0])

    # Test MAE where a `sample_weight` is not explicitly provided.
    # This is equivalent to providing uniform sample weights, though
    # the internal logic is different:
    dt_mae.fit(X=[[3], [5], [3], [8], [5]], y=[6, 7, 3, 4, 3])
    assert_array_equal(dt_mae.tree_.impurity, [1.4, 1.5, 4.0 / 3.0])
    assert_array_equal(dt_mae.tree_.value.flat, [4, 4.5, 4.0])
