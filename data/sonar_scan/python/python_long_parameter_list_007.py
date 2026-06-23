def __init__(
    self,
    kernel="rbf",
    *,
    gamma=None,
    coef0=None,
    degree=None,
    kernel_params=None,
    n_components=100,
    random_state=None,
    n_jobs=None,
):
    self.kernel = kernel
    self.gamma = gamma
    self.coef0 = coef0
    self.degree = degree
    self.kernel_params = kernel_params
    self.n_components = n_components
    self.random_state = random_state
    self.n_jobs = n_jobs
