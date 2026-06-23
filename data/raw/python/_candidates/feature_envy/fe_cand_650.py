def http_method_not_allowed(self, request, *args, **kwargs):
    logger.warning(
        "Method Not Allowed (%s): %s",
        request.method,
        request.path,
        extra={"status_code": 405, "request": request},
    )
    response = HttpResponseNotAllowed(self._allowed_methods())

    if self.view_is_async:

        async def func():
            return response

        return func()
    else:
        return response
