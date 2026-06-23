class Predictor(ABC):
    """Abstract base class for benchmarks of estimators implementing predict"""

    if Benchmark.bench_predict:

        def time_predict(self, *args):
            self.estimator.predict(self.X)

        def peakmem_predict(self, *args):
            self.estimator.predict(self.X)

        if Benchmark.base_commit is not None:

            def track_same_prediction(self, *args):
                est_path = get_estimator_path(self, Benchmark.base_commit, args, True)
                with est_path.open(mode="rb") as f:
                    estimator_base = pickle.load(f)

                y_val_pred_base = estimator_base.predict(self.X_val)
                y_val_pred = self.estimator.predict(self.X_val)

                return np.allclose(y_val_pred_base, y_val_pred)

    @property
    @abstractmethod
    def params(self):
        pass
