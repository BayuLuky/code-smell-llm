def predict(self, X, **predict_params):
    """Predict using the base regressor, applying inverse.

    The regressor is used to predict and the `inverse_func` or
    `inverse_transform` is applied before returning the prediction.

    Parameters
    ----------
    X : {array-like, sparse matrix} of shape (n_samples, n_features)
        Samples.

    **predict_params : dict of str -> object
        Parameters passed to the `predict` method of the underlying
        regressor.

    Returns
    -------
    y_hat : ndarray of shape (n_samples,)
        Predicted values.
    """
    check_is_fitted(self)
    pred = self.regressor_.predict(X, **predict_params)
    if pred.ndim == 1:
        pred_trans = self.transformer_.inverse_transform(pred.reshape(-1, 1))
    else:
        pred_trans = self.transformer_.inverse_transform(pred)
    if (
        self._training_dim == 1
        and pred_trans.ndim == 2
        and pred_trans.shape[1] == 1
    ):
        pred_trans = pred_trans.squeeze(axis=1)

    return pred_trans
