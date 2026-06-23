def _iter_test_indices(self, X, y, groups):
    if groups is None:
        raise ValueError("The 'groups' parameter should not be None.")
    groups = check_array(groups, input_name="groups", ensure_2d=False, dtype=None)

    unique_groups, groups = np.unique(groups, return_inverse=True)
    n_groups = len(unique_groups)

    if self.n_splits > n_groups:
        raise ValueError(
            "Cannot have number of splits n_splits=%d greater"
            " than the number of groups: %d." % (self.n_splits, n_groups)
        )

    # Weight groups by their number of occurrences
    n_samples_per_group = np.bincount(groups)

    # Distribute the most frequent groups first
    indices = np.argsort(n_samples_per_group)[::-1]
    n_samples_per_group = n_samples_per_group[indices]

    # Total weight of each fold
    n_samples_per_fold = np.zeros(self.n_splits)

    # Mapping from group index to fold index
    group_to_fold = np.zeros(len(unique_groups))

    # Distribute samples by adding the largest weight to the lightest fold
    for group_index, weight in enumerate(n_samples_per_group):
        lightest_fold = np.argmin(n_samples_per_fold)
        n_samples_per_fold[lightest_fold] += weight
        group_to_fold[indices[group_index]] = lightest_fold

    indices = group_to_fold[groups]

    for f in range(self.n_splits):
        yield np.where(indices == f)[0]
