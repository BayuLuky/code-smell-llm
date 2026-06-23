def __getitem__(self, key: str) -> t.Any:
    try:
        return super().__getitem__(key)
    except KeyError as e:
        if key not in request.form:
            raise

        raise DebugFilesKeyError(request, key).with_traceback(
            e.__traceback__
        ) from None
