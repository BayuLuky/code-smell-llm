def _cb_timeout(
    response: Response, request: Request, timeout: float, timeout_cl: DelayedCall
) -> Response:
    if timeout_cl.active():
        timeout_cl.cancel()
        return response

    url = urldefrag(request.url)[0]
    raise TimeoutError(f"Getting {url} took longer than {timeout} seconds.")
