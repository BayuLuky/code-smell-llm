def __init__(
    self,
    penalty="l2",
    dual=False,
    tol=1e-4,
    C=1.0,
    fit_intercept=True,
    intercept_scaling=1,
    class_weight=None,
    random_state=None,
    solver="warn",
    max_iter=100,
    multi_class="warn",
    verbose=0,
    warm_start=False,
    n_jobs=None,
    l1_ratio=None,
):
    self.penalty = penalty
    self.dual = dual
    self.tol = tol
    self.C = C
    self.fit_intercept = fit_intercept
    self.intercept_scaling = intercept_scaling
    self.class_weight = class_weight
    self.random_state = random_state
    self.solver = solver
    self.max_iter = max_iter
    self.multi_class = multi_class
    self.verbose = verbose
    self.warm_start = warm_start
    self.n_jobs = n_jobs
    self.l1_ratio = l1_ratio
