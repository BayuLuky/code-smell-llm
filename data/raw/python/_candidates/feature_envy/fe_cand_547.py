def score(self, X, y, sample_weight=None, **score_params):
    """Score using the `scoring` option on the given test data and labels.

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Test samples.

    y : array-like of shape (n_samples,)
        True labels for X.

    sample_weight : array-like of shape (n_samples,), default=None
        Sample weights.

    **score_params : dict
        Parameters to pass to the `score` method of the underlying scorer.

        .. versionadded:: 1.4

    Returns
    -------
    score : float
        Score of self.predict(X) w.r.t. y.
    """
    _raise_for_params(score_params, self, "score")

    scoring = self._get_scorer()
    if _routing_enabled():
        routed_params = process_routing(
            self,
            "score",
            sample_weight=sample_weight,
            **score_params,
        )
    else:
        routed_params = Bunch()
        routed_params.scorer = Bunch(score={})
        if sample_weight is not None:
            routed_params.scorer.score["sample_weight"] = sample_weight

    return scoring(
        self,
        X,
        y,
        **routed_params.scorer.score,
    )
