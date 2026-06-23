def _decision_function(self, X):
    # return log posterior, see eq (4.12) p. 110 of the ESL.
    check_is_fitted(self)

    X = self._validate_data(X, reset=False)
    norm2 = []
    for i in range(len(self.classes_)):
        R = self.rotations_[i]
        S = self.scalings_[i]
        Xm = X - self.means_[i]
        X2 = np.dot(Xm, R * (S ** (-0.5)))
        norm2.append(np.sum(X2**2, axis=1))
    norm2 = np.array(norm2).T  # shape = [len(X), n_classes]
    u = np.asarray([np.sum(np.log(s)) for s in self.scalings_])
    return -0.5 * (norm2 + u) + np.log(self.priors_)
