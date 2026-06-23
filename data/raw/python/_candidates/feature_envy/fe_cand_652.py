def open(
    self,
    *args: t.Any,
    buffered: bool = False,
    follow_redirects: bool = False,
    **kwargs: t.Any,
) -> TestResponse:
    if args and isinstance(
        args[0], (werkzeug.test.EnvironBuilder, dict, BaseRequest)
    ):
        if isinstance(args[0], werkzeug.test.EnvironBuilder):
            builder = copy(args[0])
            builder.environ_base = self._copy_environ(builder.environ_base or {})  # type: ignore[arg-type]
            request = builder.get_request()
        elif isinstance(args[0], dict):
            request = EnvironBuilder.from_environ(
                args[0], app=self.application, environ_base=self._copy_environ({})
            ).get_request()
        else:
            # isinstance(args[0], BaseRequest)
            request = copy(args[0])
            request.environ = self._copy_environ(request.environ)
    else:
        # request is None
        request = self._request_from_builder_args(args, kwargs)

    # Pop any previously preserved contexts. This prevents contexts
    # from being preserved across redirects or multiple requests
    # within a single block.
    self._context_stack.close()

    response = super().open(
        request,
        buffered=buffered,
        follow_redirects=follow_redirects,
    )
    response.json_module = self.application.json  # type: ignore[assignment]

    # Re-push contexts that were preserved during the request.
    while self._new_contexts:
        cm = self._new_contexts.pop()
        self._context_stack.enter_context(cm)

    return response
