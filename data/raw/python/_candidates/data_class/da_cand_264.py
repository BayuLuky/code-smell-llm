class Transformer(ABC):
    """Abstract base class for benchmarks of estimators implementing transform"""

    if Benchmark.bench_transform:

        def time_transform(self, *args):
            self.estimator.transform(self.X)

        def peakmem_transform(self, *args):
            self.estimator.transform(self.X)

        if Benchmark.base_commit is not None:

            def track_same_transform(self, *args):
                est_path = get_estimator_path(self, Benchmark.base_commit, args, True)
                with est_path.open(mode="rb") as f:
                    estimator_base = pickle.load(f)

                X_val_t_base = estimator_base.transform(self.X_val)
                X_val_t = self.estimator.transform(self.X_val)

                return np.allclose(X_val_t_base, X_val_t)

    @property
    @abstractmethod
    def params(self):
        pass
