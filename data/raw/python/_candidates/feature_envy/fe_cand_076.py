def command(  # type: ignore[override]
    self, *args: t.Any, **kwargs: t.Any
) -> t.Callable[[t.Callable[..., t.Any]], click.Command]:
    """This works exactly like the method of the same name on a regular
    :class:`click.Group` but it wraps callbacks in :func:`with_appcontext`
    unless it's disabled by passing ``with_appcontext=False``.
    """
    wrap_for_ctx = kwargs.pop("with_appcontext", True)

    def decorator(f: t.Callable[..., t.Any]) -> click.Command:
        if wrap_for_ctx:
            f = with_appcontext(f)
        return super(AppGroup, self).command(*args, **kwargs)(f)  # type: ignore[no-any-return]

    return decorator
