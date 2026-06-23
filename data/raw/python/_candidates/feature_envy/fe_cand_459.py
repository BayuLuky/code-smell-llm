def create_container(self, X_output, X_original, columns, inplace=True):
    pl = check_library_installed("polars")
    columns = get_columns(columns)
    columns = columns.tolist() if isinstance(columns, np.ndarray) else columns

    if not inplace or not isinstance(X_output, pl.DataFrame):
        # In all these cases, we need to create a new DataFrame
        return pl.DataFrame(X_output, schema=columns, orient="row")

    if columns is not None:
        return self.rename_columns(X_output, columns)
    return X_output
