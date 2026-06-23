def __init__(
    self,
    radius=1.0,
    *,
    weights="uniform",
    algorithm="auto",
    leaf_size=30,
    p=2,
    metric="minkowski",
    outlier_label=None,
    metric_params=None,
    n_jobs=None,
):
    super().__init__(
        radius=radius,
        algorithm=algorithm,
        leaf_size=leaf_size,
        metric=metric,
        p=p,
        metric_params=metric_params,
        n_jobs=n_jobs,
    )
    self.weights = weights
    self.outlier_label = outlier_label
