def __init__(
    self,
    C=1.0,
    kernel="rbf",
    degree=3,
    gamma="auto_deprecated",
    coef0=0.0,
    shrinking=True,
    probability=False,
    tol=1e-3,
    cache_size=200,
    class_weight=None,
    verbose=False,
    max_iter=-1,
    decision_function_shape="ovr",
    random_state=None,
):
    self.kernel = kernel
    self.degree = degree
    self.gamma = gamma
    self.coef0 = coef0
    self.tol = tol
    self.C = C
    self.shrinking = shrinking
    self.probability = probability
    self.cache_size = cache_size
    self.class_weight = class_weight
    self.verbose = verbose
    self.max_iter = max_iter
    self.decision_function_shape = decision_function_shape
    self.random_state = random_state
