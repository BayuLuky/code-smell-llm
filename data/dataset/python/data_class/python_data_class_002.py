class ParsingState:
    def __init__(self, rargs: t.List[str]) -> None:
        self.opts: t.Dict[str, t.Any] = {}
        self.largs: t.List[str] = []
        self.rargs = rargs
        self.order: t.List["CoreParameter"] = []
