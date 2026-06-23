def __init__(
    self,
    alpha=1.0,
    *,
    l1_ratio=0.5,
    fit_intercept=True,
    precompute=False,
    max_iter=1000,
    copy_X=True,
    tol=1e-4,
    warm_start=False,
    positive=False,
    random_state=None,
    selection="cyclic",
):
    self.alpha = alpha
    self.l1_ratio = l1_ratio
    self.fit_intercept = fit_intercept
    self.precompute = precompute
    self.max_iter = max_iter
    self.copy_X = copy_X
    self.tol = tol
    self.warm_start = warm_start
    self.positive = positive
    self.random_state = random_state
    self.selection = selection
