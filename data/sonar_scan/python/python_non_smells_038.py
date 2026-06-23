def _estimators_has(attr):
    """Check if self.estimator or self.estimators_[0] has attr.

    If `self.estimators_[0]` has the attr, then its safe to assume that other
    estimators have it too. We raise the original `AttributeError` if `attr`
    does not exist. This function is used together with `available_if`.
    """

    def check(self):
        if hasattr(self, "estimators_"):
            getattr(self.estimators_[0], attr)
        else:
            getattr(self.estimator, attr)

        return True

    return check
