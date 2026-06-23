def _threshold_for_binary_predict(estimator):
    """Threshold for predictions from binary estimator."""
    if hasattr(estimator, "decision_function") and is_classifier(estimator):
        return 0.0
    else:
        # predict_proba threshold
        return 0.5
