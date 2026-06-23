def _get_median_predict(self, X, limit):
    # Evaluate predictions of all estimators
    predictions = np.array([est.predict(X) for est in self.estimators_[:limit]]).T

    # Sort the predictions
    sorted_idx = np.argsort(predictions, axis=1)

    # Find index of median prediction for each sample
    weight_cdf = stable_cumsum(self.estimator_weights_[sorted_idx], axis=1)
    median_or_above = weight_cdf >= 0.5 * weight_cdf[:, -1][:, np.newaxis]
    median_idx = median_or_above.argmax(axis=1)

    median_estimators = sorted_idx[np.arange(_num_samples(X)), median_idx]

    # Return median predictions
    return predictions[np.arange(_num_samples(X)), median_estimators]
