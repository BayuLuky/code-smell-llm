def _prepare_response_obj(
    self, args: tuple[t.Any, ...], kwargs: dict[str, t.Any]
) -> t.Any:
    if args and kwargs:
        raise TypeError("app.json.response() takes either args or kwargs, not both")

    if not args and not kwargs:
        return None

    if len(args) == 1:
        return args[0]

    return args or kwargs
