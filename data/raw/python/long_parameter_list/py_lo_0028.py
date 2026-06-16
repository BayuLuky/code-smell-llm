def follow(
    self,
    url,
    callback=None,
    method="GET",
    headers=None,
    body=None,
    cookies=None,
    meta=None,
    encoding="utf-8",
    priority=0,
    dont_filter=False,
    errback=None,
    cb_kwargs=None,
    flags=None,
) -> Request:
    """
    Return a :class:`~.Request` instance to follow a link ``url``.
    It accepts the same arguments as ``Request.__init__`` method,
    but ``url`` can be a relative URL or a ``scrapy.link.Link`` object,
    not only an absolute URL.

    :class:`~.TextResponse` provides a :meth:`~.TextResponse.follow`
    method which supports selectors in addition to absolute/relative URLs
    and Link objects.

    .. versionadded:: 2.0
       The *flags* parameter.
    """
    if isinstance(url, Link):
        url = url.url
    elif url is None:
        raise ValueError("url can't be None")
    url = self.urljoin(url)

    return Request(
        url=url,
        callback=callback,
        method=method,
        headers=headers,
        body=body,
        cookies=cookies,
        meta=meta,
        encoding=encoding,
        priority=priority,
        dont_filter=dont_filter,
        errback=errback,
        cb_kwargs=cb_kwargs,
        flags=flags,
    )
