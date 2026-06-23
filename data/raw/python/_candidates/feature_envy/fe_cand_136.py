def hyperparameters(self):
    """Returns a list of all hyperparameter."""
    r = [
        Hyperparameter(
            "k1__" + hyperparameter.name,
            hyperparameter.value_type,
            hyperparameter.bounds,
            hyperparameter.n_elements,
        )
        for hyperparameter in self.k1.hyperparameters
    ]

    for hyperparameter in self.k2.hyperparameters:
        r.append(
            Hyperparameter(
                "k2__" + hyperparameter.name,
                hyperparameter.value_type,
                hyperparameter.bounds,
                hyperparameter.n_elements,
            )
        )
    return r
