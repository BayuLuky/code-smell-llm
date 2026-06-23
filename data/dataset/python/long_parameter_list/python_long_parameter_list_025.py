def __init__(
    self,
    estimator=None,
    *,
    min_samples=None,
    residual_threshold=None,
    is_data_valid=None,
    is_model_valid=None,
    max_trials=100,
    max_skips=np.inf,
    stop_n_inliers=np.inf,
    stop_score=np.inf,
    stop_probability=0.99,
    loss="absolute_error",
    random_state=None,
):
    self.estimator = estimator
    self.min_samples = min_samples
    self.residual_threshold = residual_threshold
    self.is_data_valid = is_data_valid
    self.is_model_valid = is_model_valid
    self.max_trials = max_trials
    self.max_skips = max_skips
    self.stop_n_inliers = stop_n_inliers
    self.stop_score = stop_score
    self.stop_probability = stop_probability
    self.random_state = random_state
    self.loss = loss
