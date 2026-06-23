def __init__(
    self,
    n_components=2,
    *,
    metric=True,
    n_init=4,
    max_iter=300,
    verbose=0,
    eps=1e-3,
    n_jobs=None,
    random_state=None,
    dissimilarity="euclidean",
    normalized_stress="auto",
):
    self.n_components = n_components
    self.dissimilarity = dissimilarity
    self.metric = metric
    self.n_init = n_init
    self.max_iter = max_iter
    self.eps = eps
    self.verbose = verbose
    self.n_jobs = n_jobs
    self.random_state = random_state
    self.normalized_stress = normalized_stress
