def __init__(
    self,
    eps=1e-3,
    n_alphas=100,
    alphas=None,
    fit_intercept=True,
    precompute="auto",
    max_iter=1000,
    tol=1e-4,
    copy_X=True,
    cv=None,
    verbose=False,
    n_jobs=None,
    positive=False,
    random_state=None,
    selection="cyclic",
):
    self.eps = eps
    self.n_alphas = n_alphas
    self.alphas = alphas
    self.fit_intercept = fit_intercept
    self.precompute = precompute
    self.max_iter = max_iter
    self.tol = tol
    self.copy_X = copy_X
    self.cv = cv
    self.verbose = verbose
    self.n_jobs = n_jobs
    self.positive = positive
    self.random_state = random_state
    self.selection = selection
