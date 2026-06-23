def __init__(
    self,
    name: t.Optional[str] = None,
    sources: t.Optional[t.List[MultiCommand]] = None,
    **attrs: t.Any,
) -> None:
    super().__init__(name, **attrs)
    #: The list of registered multi commands.
    self.sources: t.List[MultiCommand] = sources or []
