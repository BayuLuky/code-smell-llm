def convert(
    self, value: t.Any, param: t.Optional["Parameter"], ctx: t.Optional["Context"]
) -> t.Any:
    """Convert the value to the correct type. This is not called if
    the value is ``None`` (the missing value).

    This must accept string values from the command line, as well as
    values that are already the correct type. It may also convert
    other compatible types.

    The ``param`` and ``ctx`` arguments may be ``None`` in certain
    situations, such as when converting prompt input.

    If the value cannot be converted, call :meth:`fail` with a
    descriptive message.

    :param value: The value to convert.
    :param param: The parameter that is using this type to convert
        its value. May be ``None``.
    :param ctx: The current context that arrived at this value. May
        be ``None``.
    """
    return value
