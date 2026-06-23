def _transform(self, X):
    """Reduce X to the selected features."""
    mask = self.get_support()
    if not mask.any():
        warnings.warn(
            (
                "No features were selected: either the data is"
                " too noisy or the selection test too strict."
            ),
            UserWarning,
        )
        if hasattr(X, "iloc"):
            return X.iloc[:, :0]
        return np.empty(0, dtype=X.dtype).reshape((X.shape[0], 0))
    return _safe_indexing(X, mask, axis=1)
