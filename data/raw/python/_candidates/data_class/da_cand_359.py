class WeightedMetaRegressor(MetaEstimatorMixin, RegressorMixin, BaseEstimator):
    __metadata_request__fit = {"sample_weight": metadata_routing.WARN}

    def __init__(self, estimator):
        self.estimator = estimator

    def fit(self, X, y, sample_weight=None, **fit_params):
        params = process_routing(self, "fit", sample_weight=sample_weight, **fit_params)
        check_metadata(self, sample_weight=sample_weight)
        self.estimator_ = clone(self.estimator).fit(X, y, **params.estimator.fit)

    def get_metadata_routing(self):
        router = (
            MetadataRouter(owner=self.__class__.__name__)
            .add_self_request(self)
            .add(estimator=self.estimator, method_mapping="one-to-one")
        )
        return router
