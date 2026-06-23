def __init__(self, formats: t.Optional[t.Sequence[str]] = None):
    self.formats: t.Sequence[str] = formats or [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ]
