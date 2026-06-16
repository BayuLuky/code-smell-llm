def __init__(
    self,
    estimator,
    param_grid,
    scoring=None,
    n_jobs=None,
    iid="warn",
    refit=True,
    cv="warn",
    verbose=0,
    pre_dispatch="2*n_jobs",
    error_score="raise-deprecating",
    return_train_score=False,
):
    self.estimator = estimator
    self.param_grid = param_grid
    self.scoring = scoring
    self.n_jobs = n_jobs
    self.iid = iid
    self.refit = refit
    self.cv = cv
    self.verbose = verbose
    self.pre_dispatch = pre_dispatch
    self.error_score = error_score
    self.return_train_score = return_train_score
