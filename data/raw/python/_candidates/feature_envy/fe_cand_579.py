def _filter(self, request, spider):
    if isinstance(request, Request) and len(request.url) > self.maxlength:
        logger.info(
            "Ignoring link (url length > %(maxlength)d): %(url)s ",
            {"maxlength": self.maxlength, "url": request.url},
            extra={"spider": spider},
        )
        spider.crawler.stats.inc_value(
            "urllength/request_ignored_count", spider=spider
        )
        return False
    return True
