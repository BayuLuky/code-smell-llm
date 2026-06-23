def group(  # type: ignore[override]
    self, *args: t.Any, **kwargs: t.Any
) -> t.Callable[[t.Callable[..., t.Any]], click.Group]:
    """This works exactly like the method of the same name on a regular
    :class:`click.Group` but it defaults the group class to
    :class:`AppGroup`.
    """
    kwargs.setdefault("cls", AppGroup)
    return super().group(*args, **kwargs)  # type: ignore[no-any-return]
