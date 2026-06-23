def sample(self, n_samples=1, random_state=None):
    """Generate random samples from the model.

    Currently, this is implemented only for gaussian and tophat kernels.

    Parameters
    ----------
    n_samples : int, default=1
        Number of samples to generate.

    random_state : int, RandomState instance or None, default=None
        Determines random number generation used to generate
        random samples. Pass an int for reproducible results
        across multiple function calls.
        See :term:`Glossary <random_state>`.

    Returns
    -------
    X : array-like of shape (n_samples, n_features)
        List of samples.
    """
    check_is_fitted(self)
    # TODO: implement sampling for other valid kernel shapes
    if self.kernel not in ["gaussian", "tophat"]:
        raise NotImplementedError()

    data = np.asarray(self.tree_.data)

    rng = check_random_state(random_state)
    u = rng.uniform(0, 1, size=n_samples)
    if self.tree_.sample_weight is None:
        i = (u * data.shape[0]).astype(np.int64)
    else:
        cumsum_weight = np.cumsum(np.asarray(self.tree_.sample_weight))
        sum_weight = cumsum_weight[-1]
        i = np.searchsorted(cumsum_weight, u * sum_weight)
    if self.kernel == "gaussian":
        return np.atleast_2d(rng.normal(data[i], self.bandwidth_))

    elif self.kernel == "tophat":
        # we first draw points from a d-dimensional normal distribution,
        # then use an incomplete gamma function to map them to a uniform
        # d-dimensional tophat distribution.
        dim = data.shape[1]
        X = rng.normal(size=(n_samples, dim))
        s_sq = row_norms(X, squared=True)
        correction = (
            gammainc(0.5 * dim, 0.5 * s_sq) ** (1.0 / dim)
            * self.bandwidth_
            / np.sqrt(s_sq)
        )
        return data[i] + X * correction[:, np.newaxis]
