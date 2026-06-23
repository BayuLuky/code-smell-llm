class Argument:
    def __init__(self, obj: "CoreArgument", dest: t.Optional[str], nargs: int = 1):
        self.dest = dest
        self.nargs = nargs
        self.obj = obj

    def process(
        self,
        value: t.Union[t.Optional[str], t.Sequence[t.Optional[str]]],
        state: "ParsingState",
    ) -> None:
        if self.nargs > 1:
            assert value is not None
            holes = sum(1 for x in value if x is None)
            if holes == len(value):
                value = None
            elif holes != 0:
                raise BadArgumentUsage(
                    _("Argument {name!r} takes {nargs} values.").format(
                        name=self.dest, nargs=self.nargs
                    )
                )

        if self.nargs == -1 and self.obj.envvar is not None and value == ():
            # Replace empty tuple with None so that a value from the
            # environment may be tried.
            value = None

        state.opts[self.dest] = value  # type: ignore
        state.order.append(self.obj)
