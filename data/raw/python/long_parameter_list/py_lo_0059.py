def __init__(
    self,
    kernel=None,
    *,
    alpha=1e-10,
    optimizer="fmin_l_bfgs_b",
    n_restarts_optimizer=0,
    normalize_y=False,
    copy_X_train=True,
    n_targets=None,
    random_state=None,
):
    self.kernel = kernel
    self.alpha = alpha
    self.optimizer = optimizer
    self.n_restarts_optimizer = n_restarts_optimizer
    self.normalize_y = normalize_y
    self.copy_X_train = copy_X_train
    self.n_targets = n_targets
    self.random_state = random_state
