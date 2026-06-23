def fit(self, X, y=None, sample_weight=None):
    """
    Fit the estimator.

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Data to be discretized.

    y : None
        Ignored. This parameter exists only for compatibility with
        :class:`~sklearn.pipeline.Pipeline`.

    sample_weight : ndarray of shape (n_samples,)
        Contains weight values to be associated with each sample.
        Only possible when `strategy` is set to `"quantile"`.

        .. versionadded:: 1.3

    Returns
    -------
    self : object
        Returns the instance itself.
    """
    X = self._validate_data(X, dtype="numeric")

    if self.dtype in (np.float64, np.float32):
        output_dtype = self.dtype
    else:  # self.dtype is None
        output_dtype = X.dtype

    n_samples, n_features = X.shape

    if sample_weight is not None and self.strategy == "uniform":
        raise ValueError(
            "`sample_weight` was provided but it cannot be "
            "used with strategy='uniform'. Got strategy="
            f"{self.strategy!r} instead."
        )

    if self.strategy in ("uniform", "kmeans") and self.subsample == "warn":
        warnings.warn(
            (
                "In version 1.5 onwards, subsample=200_000 "
                "will be used by default. Set subsample explicitly to "
                "silence this warning in the mean time. Set "
                "subsample=None to disable subsampling explicitly."
            ),
            FutureWarning,
        )

    subsample = self.subsample
    if subsample == "warn":
        subsample = 200000 if self.strategy == "quantile" else None
    if subsample is not None and n_samples > subsample:
        rng = check_random_state(self.random_state)
        subsample_idx = rng.choice(n_samples, size=subsample, replace=False)
        X = _safe_indexing(X, subsample_idx)

    n_features = X.shape[1]
    n_bins = self._validate_n_bins(n_features)

    if sample_weight is not None:
        sample_weight = _check_sample_weight(sample_weight, X, dtype=X.dtype)

    bin_edges = np.zeros(n_features, dtype=object)
    for jj in range(n_features):
        column = X[:, jj]
        col_min, col_max = column.min(), column.max()

        if col_min == col_max:
            warnings.warn(
                "Feature %d is constant and will be replaced with 0." % jj
            )
            n_bins[jj] = 1
            bin_edges[jj] = np.array([-np.inf, np.inf])
            continue

        if self.strategy == "uniform":
            bin_edges[jj] = np.linspace(col_min, col_max, n_bins[jj] + 1)

        elif self.strategy == "quantile":
            quantiles = np.linspace(0, 100, n_bins[jj] + 1)
            if sample_weight is None:
                bin_edges[jj] = np.asarray(np.percentile(column, quantiles))
            else:
                bin_edges[jj] = np.asarray(
                    [
                        _weighted_percentile(column, sample_weight, q)
                        for q in quantiles
                    ],
                    dtype=np.float64,
                )
        elif self.strategy == "kmeans":
            from ..cluster import KMeans  # fixes import loops

            # Deterministic initialization with uniform spacing
            uniform_edges = np.linspace(col_min, col_max, n_bins[jj] + 1)
            init = (uniform_edges[1:] + uniform_edges[:-1])[:, None] * 0.5

            # 1D k-means procedure
            km = KMeans(n_clusters=n_bins[jj], init=init, n_init=1)
            centers = km.fit(
                column[:, None], sample_weight=sample_weight
            ).cluster_centers_[:, 0]
            # Must sort, centers may be unsorted even with sorted init
            centers.sort()
            bin_edges[jj] = (centers[1:] + centers[:-1]) * 0.5
            bin_edges[jj] = np.r_[col_min, bin_edges[jj], col_max]

        # Remove bins whose width are too small (i.e., <= 1e-8)
        if self.strategy in ("quantile", "kmeans"):
            mask = np.ediff1d(bin_edges[jj], to_begin=np.inf) > 1e-8
            bin_edges[jj] = bin_edges[jj][mask]
            if len(bin_edges[jj]) - 1 != n_bins[jj]:
                warnings.warn(
                    "Bins whose width are too small (i.e., <= "
                    "1e-8) in feature %d are removed. Consider "
                    "decreasing the number of bins." % jj
                )
                n_bins[jj] = len(bin_edges[jj]) - 1

    self.bin_edges_ = bin_edges
    self.n_bins_ = n_bins

    if "onehot" in self.encode:
        self._encoder = OneHotEncoder(
            categories=[np.arange(i) for i in self.n_bins_],
            sparse_output=self.encode == "onehot",
            dtype=output_dtype,
        )
        # Fit the OneHotEncoder with toy datasets
        # so that it's ready for use after the KBinsDiscretizer is fitted
        self._encoder.fit(np.zeros((1, len(self.n_bins_))))

    return self
