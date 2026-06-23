def __call__(
    self,
    value: t.Any,
    param: t.Optional["Parameter"] = None,
    ctx: t.Optional["Context"] = None,
) -> t.Any:
    if value is not None:
        return self.convert(value, param, ctx)
