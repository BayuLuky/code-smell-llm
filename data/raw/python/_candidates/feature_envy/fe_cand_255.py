def create_container(self, X_output, X_original, columns, inplace=True):
    pd = check_library_installed("pandas")
    columns = get_columns(columns)

    if not inplace or not isinstance(X_output, pd.DataFrame):
        # In all these cases, we need to create a new DataFrame

        # Unfortunately, we cannot use `getattr(container, "index")`
        # because `list` exposes an `index` attribute.
        if isinstance(X_output, pd.DataFrame):
            index = X_output.index
        elif isinstance(X_original, pd.DataFrame):
            index = X_original.index
        else:
            index = None

        # We don't pass columns here because it would intend columns selection
        # instead of renaming.
        X_output = pd.DataFrame(X_output, index=index, copy=not inplace)

    if columns is not None:
        return self.rename_columns(X_output, columns)
    return X_output
