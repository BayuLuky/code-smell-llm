def convert(
    self, value: t.Any, param: t.Optional["Parameter"], ctx: t.Optional["Context"]
) -> t.Any:
    if value in {False, True}:
        return bool(value)

    norm = value.strip().lower()

    if norm in {"1", "true", "t", "yes", "y", "on"}:
        return True

    if norm in {"0", "false", "f", "no", "n", "off"}:
        return False

    self.fail(
        _("{value!r} is not a valid boolean.").format(value=value), param, ctx
    )
