def convert(
    self, value: t.Any, param: t.Optional["Parameter"], ctx: t.Optional["Context"]
) -> t.Any:
    import uuid

    if isinstance(value, uuid.UUID):
        return value

    value = value.strip()

    try:
        return uuid.UUID(value)
    except ValueError:
        self.fail(
            _("{value!r} is not a valid UUID.").format(value=value), param, ctx
        )
