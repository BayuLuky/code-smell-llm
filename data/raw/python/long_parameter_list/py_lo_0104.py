def __init__(
    self,
    alpha=1.0,
    *,
    fit_intercept=True,
    copy_X=True,
    max_iter=1000,
    tol=1e-4,
    warm_start=False,
    random_state=None,
    selection="cyclic",
):
    self.alpha = alpha
    self.fit_intercept = fit_intercept
    self.max_iter = max_iter
    self.copy_X = copy_X
    self.tol = tol
    self.warm_start = warm_start
    self.l1_ratio = 1.0
    self.random_state = random_state
    self.selection = selection
