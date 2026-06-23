class _SubsampleMetaSplitter:
    """Splitter that subsamples a given fraction of the dataset"""

    def __init__(self, *, base_cv, fraction, subsample_test, random_state):
        self.base_cv = base_cv
        self.fraction = fraction
        self.subsample_test = subsample_test
        self.random_state = random_state

    def split(self, X, y, **kwargs):
        for train_idx, test_idx in self.base_cv.split(X, y, **kwargs):
            train_idx = resample(
                train_idx,
                replace=False,
                random_state=self.random_state,
                n_samples=int(self.fraction * len(train_idx)),
            )
            if self.subsample_test:
                test_idx = resample(
                    test_idx,
                    replace=False,
                    random_state=self.random_state,
                    n_samples=int(self.fraction * len(test_idx)),
                )
            yield train_idx, test_idx
