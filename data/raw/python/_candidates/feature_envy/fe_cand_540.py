def predict(self, X, **predict_params):
    check_is_fitted(self)
    # same as in ``fit``, we validate the given metadata
    request_router = get_routing_for_object(self)
    request_router.validate_metadata(params=predict_params, method="predict")
    # and then prepare the input to the underlying ``predict`` method.
    params = request_router.route_params(params=predict_params, caller="predict")
    return self.estimator_.predict(X, **params.estimator.predict)
