def _weighted_cluster_center(self, X):
    """Calculate and store the centroids/medoids of each cluster.

    This requires `X` to be a raw feature array, not precomputed
    distances. Rather than return outputs directly, this helper method
    instead stores them in the `self.{centroids, medoids}_` attributes.
    The choice for which attributes are calculated and stored is mediated
    by the value of `self.store_centers`.

    Parameters
    ----------
    X : ndarray of shape (n_samples, n_features)
        The feature array that the estimator was fit with.

    """
    # Number of non-noise clusters
    n_clusters = len(set(self.labels_) - {-1, -2})
    mask = np.empty((X.shape[0],), dtype=np.bool_)
    make_centroids = self.store_centers in ("centroid", "both")
    make_medoids = self.store_centers in ("medoid", "both")

    if make_centroids:
        self.centroids_ = np.empty((n_clusters, X.shape[1]), dtype=np.float64)
    if make_medoids:
        self.medoids_ = np.empty((n_clusters, X.shape[1]), dtype=np.float64)

    # Need to handle iteratively seen each cluster may have a different
    # number of samples, hence we can't create a homogeneous 3D array.
    for idx in range(n_clusters):
        mask = self.labels_ == idx
        data = X[mask]
        strength = self.probabilities_[mask]
        if make_centroids:
            self.centroids_[idx] = np.average(data, weights=strength, axis=0)
        if make_medoids:
            # TODO: Implement weighted argmin PWD backend
            dist_mat = pairwise_distances(
                data, metric=self.metric, **self._metric_params
            )
            dist_mat = dist_mat * strength
            medoid_index = np.argmin(dist_mat.sum(axis=1))
            self.medoids_[idx] = data[medoid_index]
    return
