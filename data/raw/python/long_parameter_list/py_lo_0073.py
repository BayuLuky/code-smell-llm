def __init__(
    self,
    n_components=None,
    *,
    kernel="linear",
    gamma=None,
    degree=3,
    coef0=1,
    kernel_params=None,
    alpha=1.0,
    fit_inverse_transform=False,
    eigen_solver="auto",
    tol=0,
    max_iter=None,
    iterated_power="auto",
    remove_zero_eig=False,
    random_state=None,
    copy_X=True,
    n_jobs=None,
):
    self.n_components = n_components
    self.kernel = kernel
    self.kernel_params = kernel_params
    self.gamma = gamma
    self.degree = degree
    self.coef0 = coef0
    self.alpha = alpha
    self.fit_inverse_transform = fit_inverse_transform
    self.eigen_solver = eigen_solver
    self.tol = tol
    self.max_iter = max_iter
    self.iterated_power = iterated_power
    self.remove_zero_eig = remove_zero_eig
    self.random_state = random_state
    self.n_jobs = n_jobs
    self.copy_X = copy_X
