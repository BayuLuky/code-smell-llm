def _joint_log_likelihood(self, X):
    joint_log_likelihood = []
    for i in range(np.size(self.classes_)):
        jointi = np.log(self.class_prior_[i])
        n_ij = -0.5 * np.sum(np.log(2.0 * np.pi * self.var_[i, :]))
        n_ij -= 0.5 * np.sum(((X - self.theta_[i, :]) ** 2) / (self.var_[i, :]), 1)
        joint_log_likelihood.append(jointi + n_ij)

    joint_log_likelihood = np.array(joint_log_likelihood).T
    return joint_log_likelihood
