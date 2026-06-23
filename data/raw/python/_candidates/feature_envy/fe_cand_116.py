def score(self, X, y, sample_weight=None):
    """Compute D^2, the percentage of deviance explained.

    D^2 is a generalization of the coefficient of determination R^2.
    R^2 uses squared error and D^2 uses the deviance of this GLM, see the
    :ref:`User Guide <regression_metrics>`.

    D^2 is defined as
    :math:`D^2 = 1-\\frac{D(y_{true},y_{pred})}{D_{null}}`,
    :math:`D_{null}` is the null deviance, i.e. the deviance of a model
    with intercept alone, which corresponds to :math:`y_{pred} = \\bar{y}`.
    The mean :math:`\\bar{y}` is averaged by sample_weight.
    Best possible score is 1.0 and it can be negative (because the model
    can be arbitrarily worse).

    Parameters
    ----------
    X : {array-like, sparse matrix} of shape (n_samples, n_features)
        Test samples.

    y : array-like of shape (n_samples,)
        True values of target.

    sample_weight : array-like of shape (n_samples,), default=None
        Sample weights.

    Returns
    -------
    score : float
        D^2 of self.predict(X) w.r.t. y.
    """
    # TODO: Adapt link to User Guide in the docstring, once
    # https://github.com/scikit-learn/scikit-learn/pull/22118 is merged.
    #
    # Note, default score defined in RegressorMixin is R^2 score.
    # TODO: make D^2 a score function in module metrics (and thereby get
    #       input validation and so on)
    raw_prediction = self._linear_predictor(X)  # validates X
    # required by losses
    y = check_array(y, dtype=raw_prediction.dtype, order="C", ensure_2d=False)

    if sample_weight is not None:
        # Note that _check_sample_weight calls check_array(order="C") required by
        # losses.
        sample_weight = _check_sample_weight(sample_weight, X, dtype=y.dtype)

    base_loss = self._base_loss

    if not base_loss.in_y_true_range(y):
        raise ValueError(
            "Some value(s) of y are out of the valid range of the loss"
            f" {base_loss.__name__}."
        )

    constant = np.average(
        base_loss.constant_to_optimal_zero(y_true=y, sample_weight=None),
        weights=sample_weight,
    )

    # Missing factor of 2 in deviance cancels out.
    deviance = base_loss(
        y_true=y,
        raw_prediction=raw_prediction,
        sample_weight=sample_weight,
        n_threads=1,
    )
    y_mean = base_loss.link.link(np.average(y, weights=sample_weight))
    deviance_null = base_loss(
        y_true=y,
        raw_prediction=np.tile(y_mean, y.shape[0]),
        sample_weight=sample_weight,
        n_threads=1,
    )
    return 1 - (deviance + constant) / (deviance_null + constant)
