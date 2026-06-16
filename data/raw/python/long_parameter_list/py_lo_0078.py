def __init__(
    self,
    n_components=2,
    *,
    affinity="nearest_neighbors",
    gamma=None,
    random_state=None,
    eigen_solver=None,
    eigen_tol="auto",
    n_neighbors=None,
    n_jobs=None,
):
    self.n_components = n_components
    self.affinity = affinity
    self.gamma = gamma
    self.random_state = random_state
    self.eigen_solver = eigen_solver
    self.eigen_tol = eigen_tol
    self.n_neighbors = n_neighbors
    self.n_jobs = n_jobs
