def fit(self, X, y, **fit_params):
    """Fit underlying estimators.

    Parameters
    ----------
    X : {array-like, sparse matrix} of shape (n_samples, n_features)
        Data.

    y : array-like of shape (n_samples,)
        Multi-class targets.

    **fit_params : dict
        Parameters passed to the ``estimator.fit`` method of each
        sub-estimator.

        .. versionadded:: 1.4
            Only available if `enable_metadata_routing=True`. See
            :ref:`Metadata Routing User Guide <metadata_routing>` for more
            details.

    Returns
    -------
    self : object
        The fitted underlying estimator.
    """
    _raise_for_params(fit_params, self, "fit")

    routed_params = process_routing(
        self,
        "fit",
        **fit_params,
    )

    # We need to validate the data because we do a safe_indexing later.
    X, y = self._validate_data(
        X, y, accept_sparse=["csr", "csc"], force_all_finite=False
    )
    check_classification_targets(y)

    self.classes_ = np.unique(y)
    if len(self.classes_) == 1:
        raise ValueError(
            "OneVsOneClassifier can not be fit when only one class is present."
        )
    n_classes = self.classes_.shape[0]
    estimators_indices = list(
        zip(
            *(
                Parallel(n_jobs=self.n_jobs)(
                    delayed(_fit_ovo_binary)(
                        self.estimator,
                        X,
                        y,
                        self.classes_[i],
                        self.classes_[j],
                        fit_params=routed_params.estimator.fit,
                    )
                    for i in range(n_classes)
                    for j in range(i + 1, n_classes)
                )
            )
        )
    )

    self.estimators_ = estimators_indices[0]

    pairwise = self._get_tags()["pairwise"]
    self.pairwise_indices_ = estimators_indices[1] if pairwise else None

    return self
