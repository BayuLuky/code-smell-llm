def _get_oob_predictions(tree, X):
    """Compute the OOB predictions for an individual tree.

    Parameters
    ----------
    tree : DecisionTreeRegressor object
        A single decision tree regressor.
    X : ndarray of shape (n_samples, n_features)
        The OOB samples.

    Returns
    -------
    y_pred : ndarray of shape (n_samples, 1, n_outputs)
        The OOB associated predictions.
    """
    y_pred = tree.predict(X, check_input=False)
    if y_pred.ndim == 1:
        # single output regression
        y_pred = y_pred[:, np.newaxis, np.newaxis]
    else:
        # multioutput regression
        y_pred = y_pred[:, np.newaxis, :]
    return y_pred
