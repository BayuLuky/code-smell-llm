def _request_from_builder_args(
    self, args: tuple[t.Any, ...], kwargs: dict[str, t.Any]
) -> BaseRequest:
    kwargs["environ_base"] = self._copy_environ(kwargs.get("environ_base", {}))
    builder = EnvironBuilder(self.application, *args, **kwargs)

    try:
        return builder.get_request()
    finally:
        builder.close()
