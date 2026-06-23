def __init__(self, request: Request) -> None:
    exc = request.routing_exception
    assert isinstance(exc, RequestRedirect)
    buf = [
        f"A request was sent to '{request.url}', but routing issued"
        f" a redirect to the canonical URL '{exc.new_url}'."
    ]

    if f"{request.base_url}/" == exc.new_url.partition("?")[0]:
        buf.append(
            " The URL was defined with a trailing slash. Flask"
            " will redirect to the URL with a trailing slash if it"
            " was accessed without one."
        )

    buf.append(
        " Send requests to the canonical URL, or use 307 or 308 for"
        " routing redirects. Otherwise, browsers will drop form"
        " data.\n\n"
        "This exception is only raised in debug mode."
    )
    super().__init__("".join(buf))
