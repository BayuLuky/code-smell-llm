def __init__(
    self,
    n_components=None,
    init=None,
    solver="cd",
    beta_loss="frobenius",
    tol=1e-4,
    max_iter=200,
    random_state=None,
    alpha=0.0,
    l1_ratio=0.0,
    verbose=0,
    shuffle=False,
):
    self.n_components = n_components
    self.init = init
    self.solver = solver
    self.beta_loss = beta_loss
    self.tol = tol
    self.max_iter = max_iter
    self.random_state = random_state
    self.alpha = alpha
    self.l1_ratio = l1_ratio
    self.verbose = verbose
    self.shuffle = shuffle
