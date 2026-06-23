def __exit__(self, exc_type: t.Optional[t.Type[BaseException]], *_: t.Any) -> None:
    self.close(delete=exc_type is not None)
