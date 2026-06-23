def __init__(
    self,
    stream: t.BinaryIO,
    encoding: t.Optional[str],
    errors: t.Optional[str],
    force_readable: bool = False,
    force_writable: bool = False,
    **extra: t.Any,
) -> None:
    self._stream = stream = t.cast(
        t.BinaryIO, _FixupStream(stream, force_readable, force_writable)
    )
    super().__init__(stream, encoding, errors, **extra)
