def predict_proba(self, X):
    """Return probability estimates for the test vector X.

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features) or list of object
        Query points where the GP is evaluated for classification.

    Returns
    -------
    C : array-like of shape (n_samples, n_classes)
        Returns the probability of the samples for each class in
        the model. The columns correspond to the classes in sorted
        order, as they appear in the attribute ``classes_``.
    """
    check_is_fitted(self)

    # Based on Algorithm 3.2 of GPML
    K_star = self.kernel_(self.X_train_, X)  # K_star =k(x_star)
    f_star = K_star.T.dot(self.y_train_ - self.pi_)  # Line 4
    v = solve(self.L_, self.W_sr_[:, np.newaxis] * K_star)  # Line 5
    # Line 6 (compute np.diag(v.T.dot(v)) via einsum)
    var_f_star = self.kernel_.diag(X) - np.einsum("ij,ij->j", v, v)

    # Line 7:
    # Approximate \int log(z) * N(z | f_star, var_f_star)
    # Approximation is due to Williams & Barber, "Bayesian Classification
    # with Gaussian Processes", Appendix A: Approximate the logistic
    # sigmoid by a linear combination of 5 error functions.
    # For information on how this integral can be computed see
    # blitiri.blogspot.de/2012/11/gaussian-integral-of-error-function.html
    alpha = 1 / (2 * var_f_star)
    gamma = LAMBDAS * f_star
    integrals = (
        np.sqrt(np.pi / alpha)
        * erf(gamma * np.sqrt(alpha / (alpha + LAMBDAS**2)))
        / (2 * np.sqrt(var_f_star * 2 * np.pi))
    )
    pi_star = (COEFS * integrals).sum(axis=0) + 0.5 * COEFS.sum()

    return np.vstack((1 - pi_star, pi_star)).T
