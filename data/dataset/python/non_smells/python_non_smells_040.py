def check(self):
    if hasattr(self, "estimators_"):
        getattr(self.estimators_[0], attr)
    else:
        getattr(self.estimator, attr)

    return True
