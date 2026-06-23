def get_feature_names_out(self, input_features=None):
    """Get output feature names for transformation.

    Parameters
    ----------
    input_features : array-like of str or None, default=None
        Input features.

        - If `input_features is None`, then `feature_names_in_` is
          used as feature names in. If `feature_names_in_` is not defined,
          then the following input feature names are generated:
          `["x0", "x1", ..., "x(n_features_in_ - 1)"]`.
        - If `input_features` is an array-like, then `input_features` must
          match `feature_names_in_` if `feature_names_in_` is defined.

    Returns
    -------
    feature_names_out : ndarray of str objects
        Transformed feature names.
    """
    powers = self.powers_
    input_features = _check_feature_names_in(self, input_features)
    feature_names = []
    for row in powers:
        inds = np.where(row)[0]
        if len(inds):
            name = " ".join(
                (
                    "%s^%d" % (input_features[ind], exp)
                    if exp != 1
                    else input_features[ind]
                )
                for ind, exp in zip(inds, row[inds])
            )
        else:
            name = "1"
        feature_names.append(name)
    return np.asarray(feature_names, dtype=object)
