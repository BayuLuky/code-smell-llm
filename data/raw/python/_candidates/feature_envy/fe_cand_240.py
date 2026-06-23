def predict_proba(self, raw_prediction):
    """Predict probabilities.

    Parameters
    ----------
    raw_prediction : array of shape (n_samples,) or (n_samples, 1)
        Raw prediction values (in link space).

    Returns
    -------
    proba : array of shape (n_samples, 2)
        Element-wise class probabilities.
    """
    # Be graceful to shape (n_samples, 1) -> (n_samples,)
    if raw_prediction.ndim == 2 and raw_prediction.shape[1] == 1:
        raw_prediction = raw_prediction.squeeze(1)
    proba = np.empty((raw_prediction.shape[0], 2), dtype=raw_prediction.dtype)
    proba[:, 1] = self.link.inverse(raw_prediction)
    proba[:, 0] = 1 - proba[:, 1]
    return proba
