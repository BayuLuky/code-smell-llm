def convert(
    self, value: t.Any, param: t.Optional["Parameter"], ctx: t.Optional["Context"]
) -> t.Any:
    len_type = len(self.types)
    len_value = len(value)

    if len_value != len_type:
        self.fail(
            ngettext(
                "{len_type} values are required, but {len_value} was given.",
                "{len_type} values are required, but {len_value} were given.",
                len_value,
            ).format(len_type=len_type, len_value=len_value),
            param=param,
            ctx=ctx,
        )

    return tuple(ty(x, param, ctx) for ty, x in zip(self.types, value))
