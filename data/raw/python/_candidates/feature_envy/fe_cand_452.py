def _concatenate_indicator(self, X_imputed, X_indicator):
    """Concatenate indicator mask with the imputed data."""
    if not self.add_indicator:
        return X_imputed

    if sp.issparse(X_imputed):
        # sp.hstack may result in different formats between sparse arrays and
        # matrices; specify the format to keep consistent behavior
        hstack = partial(sp.hstack, format=X_imputed.format)
    else:
        hstack = np.hstack

    if X_indicator is None:
        raise ValueError(
            "Data from the missing indicator are not provided. Call "
            "_fit_indicator and _transform_indicator in the imputer "
            "implementation."
        )

    return hstack((X_imputed, X_indicator))
