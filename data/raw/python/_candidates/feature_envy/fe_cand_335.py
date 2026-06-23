def _select_best_index(refit, refit_metric, results):
    """Custom refit callable to return the index of the best candidate.

    We want the best candidate out of the last iteration. By default
    BaseSearchCV would return the best candidate out of all iterations.

    Currently, we only support for a single metric thus `refit` and
    `refit_metric` are not required.
    """
    last_iter = np.max(results["iter"])
    last_iter_indices = np.flatnonzero(results["iter"] == last_iter)

    test_scores = results["mean_test_score"][last_iter_indices]
    # If all scores are NaNs there is no way to pick between them,
    # so we (arbitrarily) declare the zero'th entry the best one
    if np.isnan(test_scores).all():
        best_idx = 0
    else:
        best_idx = np.nanargmax(test_scores)

    return last_iter_indices[best_idx]
