def _update_feature_log_prob(self, alpha):
    """Apply smoothing to raw counts and recompute log probabilities"""
    smoothed_fc = self.feature_count_ + alpha
    smoothed_cc = smoothed_fc.sum(axis=1)

    self.feature_log_prob_ = np.log(smoothed_fc) - np.log(
        smoothed_cc.reshape(-1, 1)
    )
