def __init__(
    self,
    *,
    l1_ratio=0.5,
    eps=1e-3,
    n_alphas=100,
    alphas=None,
    fit_intercept=True,
    max_iter=1000,
    tol=1e-4,
    cv=None,
    copy_X=True,
    verbose=0,
    n_jobs=None,
    random_state=None,
    selection="cyclic",
):
    self.l1_ratio = l1_ratio
    self.eps = eps
    self.n_alphas = n_alphas
    self.alphas = alphas
    self.fit_intercept = fit_intercept
    self.max_iter = max_iter
    self.tol = tol
    self.cv = cv
    self.copy_X = copy_X
    self.verbose = verbose
    self.n_jobs = n_jobs
    self.random_state = random_state
    self.selection = selection
