def setup_cache(self):
    """Pickle a fitted estimator for all combinations of parameters"""
    # This is run once per benchmark class.

    clear_tmp()

    param_grid = list(itertools.product(*self.params))

    for params in param_grid:
        if self.skip(params):
            continue

        estimator = self.make_estimator(params)
        X, _, y, _ = self.make_data(params)

        estimator.fit(X, y)

        est_path = get_estimator_path(
            self, Benchmark.save_dir, params, Benchmark.save_estimators
        )
        with est_path.open(mode="wb") as f:
            pickle.dump(estimator, f)
