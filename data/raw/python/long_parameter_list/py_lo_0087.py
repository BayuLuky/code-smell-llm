def __init__(
    self,
    kernel=None,
    *,
    optimizer="fmin_l_bfgs_b",
    n_restarts_optimizer=0,
    max_iter_predict=100,
    warm_start=False,
    copy_X_train=True,
    random_state=None,
    multi_class="one_vs_rest",
    n_jobs=None,
):
    self.kernel = kernel
    self.optimizer = optimizer
    self.n_restarts_optimizer = n_restarts_optimizer
    self.max_iter_predict = max_iter_predict
    self.warm_start = warm_start
    self.copy_X_train = copy_X_train
    self.random_state = random_state
    self.multi_class = multi_class
    self.n_jobs = n_jobs
