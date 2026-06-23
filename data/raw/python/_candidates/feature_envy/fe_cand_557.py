def _set_params(self, attr, **params):
    # Ensure strict ordering of parameter setting:
    # 1. All steps
    if attr in params:
        setattr(self, attr, params.pop(attr))
    # 2. Replace items with estimators in params
    items = getattr(self, attr)
    if isinstance(items, list) and items:
        # Get item names used to identify valid names in params
        # `zip` raises a TypeError when `items` does not contains
        # elements of length 2
        with suppress(TypeError):
            item_names, _ = zip(*items)
            for name in list(params.keys()):
                if "__" not in name and name in item_names:
                    self._replace_estimator(attr, name, params.pop(name))

    # 3. Step parameters and other initialisation arguments
    super().set_params(**params)
    return self
