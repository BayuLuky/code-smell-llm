def __exit__(
    self,
    exc_type: t.Optional[t.Type[BaseException]],
    exc_value: t.Optional[BaseException],
    tb: t.Optional[TracebackType],
) -> None:
    self.close_intelligently()
