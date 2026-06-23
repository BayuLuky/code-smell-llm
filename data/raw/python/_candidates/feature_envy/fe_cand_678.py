def process_request_2(self, rp, request, spider):
    if rp is None:
        return

    useragent = self._robotstxt_useragent
    if not useragent:
        useragent = request.headers.get(b"User-Agent", self._default_useragent)
    if not rp.allowed(request.url, useragent):
        logger.debug(
            "Forbidden by robots.txt: %(request)s",
            {"request": request},
            extra={"spider": spider},
        )
        self.crawler.stats.inc_value("robotstxt/forbidden")
        raise IgnoreRequest("Forbidden by robots.txt")
