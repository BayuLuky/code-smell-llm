def __init__(
    self,
    param_decls: t.Sequence[str],
    required: t.Optional[bool] = None,
    **attrs: t.Any,
) -> None:
    if required is None:
        if attrs.get("default") is not None:
            required = False
        else:
            required = attrs.get("nargs", 1) > 0

    if "multiple" in attrs:
        raise TypeError("__init__() got an unexpected keyword argument 'multiple'.")

    super().__init__(param_decls, required=required, **attrs)

    if __debug__:
        if self.default is not None and self.nargs == -1:
            raise TypeError("'default' is not supported for nargs=-1.")
