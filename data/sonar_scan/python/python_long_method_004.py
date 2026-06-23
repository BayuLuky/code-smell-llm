def partial_fit(self, X, y, classes=None, **partial_fit_params):
    """Partially fit underlying estimators.

    Should be used when memory is inefficient to train all data. Chunks
    of data can be passed in several iteration, where the first call
    should have an array of all target variables.

    Parameters
    ----------
    X : {array-like, sparse matrix) of shape (n_samples, n_features)
        Data.

    y : array-like of shape (n_samples,)
        Multi-class targets.

    classes : array, shape (n_classes, )
        Classes across all calls to partial_fit.
        Can be obtained via `np.unique(y_all)`, where y_all is the
        target vector of the entire dataset.
        This argument is only required in the first call of partial_fit
        and can be omitted in the subsequent calls.

    **partial_fit_params : dict
        Parameters passed to the ``estimator.partial_fit`` method of each
        sub-estimator.

        .. versionadded:: 1.4
            Only available if `enable_metadata_routing=True`. See
            :ref:`Metadata Routing User Guide <metadata_routing>` for more
            details.

    Returns
    -------
    self : object
        The partially fitted underlying estimator.
    """
    _raise_for_params(partial_fit_params, self, "partial_fit")

    routed_params = process_routing(
        self,
        "partial_fit",
        **partial_fit_params,
    )

    first_call = _check_partial_fit_first_call(self, classes)
    if first_call:
        self.estimators_ = [
            clone(self.estimator)
            for _ in range(self.n_classes_ * (self.n_classes_ - 1) // 2)
        ]

    if len(np.setdiff1d(y, self.classes_)):
        raise ValueError(
            "Mini-batch contains {0} while it must be subset of {1}".format(
                np.unique(y), self.classes_
            )
        )

    X, y = self._validate_data(
        X,
        y,
        accept_sparse=["csr", "csc"],
        force_all_finite=False,
        reset=first_call,
    )
    check_classification_targets(y)
    combinations = itertools.combinations(range(self.n_classes_), 2)
    self.estimators_ = Parallel(n_jobs=self.n_jobs)(
        delayed(_partial_fit_ovo_binary)(
            estimator,
            X,
            y,
            self.classes_[i],
            self.classes_[j],
            partial_fit_params=routed_params.estimator.partial_fit,
        )
        for estimator, (i, j) in zip(self.estimators_, (combinations))
    )

    self.pairwise_indices_ = None

    if hasattr(self.estimators_[0], "n_features_in_"):
        self.n_features_in_ = self.estimators_[0].n_features_in_

    return self
