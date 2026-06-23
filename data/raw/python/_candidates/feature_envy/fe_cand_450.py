def _compute_partial_dependence_recursion(self, grid, target_features):
    """Fast partial dependence computation.

    Parameters
    ----------
    grid : ndarray of shape (n_samples, n_target_features)
        The grid points on which the partial dependence should be
        evaluated.
    target_features : ndarray of shape (n_target_features)
        The set of target features for which the partial dependence
        should be evaluated.

    Returns
    -------
    averaged_predictions : ndarray of shape (n_samples,)
        The value of the partial dependence function on each grid point.
    """
    grid = np.asarray(grid, dtype=DTYPE, order="C")
    averaged_predictions = np.zeros(
        shape=grid.shape[0], dtype=np.float64, order="C"
    )

    for tree in self.estimators_:
        # Note: we don't sum in parallel because the GIL isn't released in
        # the fast method.
        tree.tree_.compute_partial_dependence(
            grid, target_features, averaged_predictions
        )
    # Average over the forest
    averaged_predictions /= len(self.estimators_)

    return averaged_predictions
