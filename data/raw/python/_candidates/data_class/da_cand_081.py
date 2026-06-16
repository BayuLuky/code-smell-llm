class BaseGraphicalLasso(EmpiricalCovariance):
    _parameter_constraints: dict = {
        **EmpiricalCovariance._parameter_constraints,
        "tol": [Interval(Real, 0, None, closed="right")],
        "enet_tol": [Interval(Real, 0, None, closed="right")],
        "max_iter": [Interval(Integral, 0, None, closed="left")],
        "mode": [StrOptions({"cd", "lars"})],
        "verbose": ["verbose"],
        "eps": [Interval(Real, 0, None, closed="both")],
    }
    _parameter_constraints.pop("store_precision")

    def __init__(
        self,
        tol=1e-4,
        enet_tol=1e-4,
        max_iter=100,
        mode="cd",
        verbose=False,
        eps=np.finfo(np.float64).eps,
        assume_centered=False,
    ):
        super().__init__(assume_centered=assume_centered)
        self.tol = tol
        self.enet_tol = enet_tol
        self.max_iter = max_iter
        self.mode = mode
        self.verbose = verbose
        self.eps = eps
