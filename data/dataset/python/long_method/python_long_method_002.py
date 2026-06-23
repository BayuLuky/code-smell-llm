def partial_fit(self, X, y, classes=None, **partial_fit_params):
    """Partially fit underlying estimators.

    Should be used when memory is inefficient to train all data.
    Chunks of data can be passed in several iterations.

    Parameters
    ----------
    X : {array-like, sparse matrix} of shape (n_samples, n_features)
        Data.

    y : {array-like, sparse matrix} of shape (n_samples,) or (n_samples, n_classes)
        Multi-class targets. An indicator matrix turns on multilabel
        classification.

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
        Instance of partially fitted estimator.
    """
    _raise_for_params(partial_fit_params, self, "partial_fit")

    routed_params = process_routing(
        self,
        "partial_fit",
        **partial_fit_params,
    )

    if _check_partial_fit_first_call(self, classes):
        self.estimators_ = [clone(self.estimator) for _ in range(self.n_classes_)]

        # A sparse LabelBinarizer, with sparse_output=True, has been
        # shown to outperform or match a dense label binarizer in all
        # cases and has also resulted in less or equal memory consumption
        # in the fit_ovr function overall.
        self.label_binarizer_ = LabelBinarizer(sparse_output=True)
        self.label_binarizer_.fit(self.classes_)

    if len(np.setdiff1d(y, self.classes_)):
        raise ValueError(
            (
                "Mini-batch contains {0} while classes " + "must be subset of {1}"
            ).format(np.unique(y), self.classes_)
        )

    Y = self.label_binarizer_.transform(y)
    Y = Y.tocsc()
    columns = (col.toarray().ravel() for col in Y.T)

    self.estimators_ = Parallel(n_jobs=self.n_jobs)(
        delayed(_partial_fit_binary)(
            estimator,
            X,
            column,
            partial_fit_params=routed_params.estimator.partial_fit,
        )
        for estimator, column in zip(self.estimators_, columns)
    )

    if hasattr(self.estimators_[0], "n_features_in_"):
        self.n_features_in_ = self.estimators_[0].n_features_in_

    return self
