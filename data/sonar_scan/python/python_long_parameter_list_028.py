def __init__(
    self,
    n_neighbors=5,
    *,
    weights="uniform",
    algorithm="auto",
    leaf_size=30,
    p=2,
    metric="minkowski",
    metric_params=None,
    n_jobs=None,
):
    super().__init__(
        n_neighbors=n_neighbors,
        algorithm=algorithm,
        leaf_size=leaf_size,
        metric=metric,
        p=p,
        metric_params=metric_params,
        n_jobs=n_jobs,
    )
    self.weights = weights
