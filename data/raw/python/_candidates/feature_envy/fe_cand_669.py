def predict_proba(self, X):
    check_is_fitted(self)
    X = check_array(X)
    proba_shape = (X.shape[0], self.classes_.size)
    y_proba = np.zeros(shape=proba_shape, dtype=np.float64)
    y_proba[:, self._most_frequent_class_idx] = 1.0
    return y_proba
