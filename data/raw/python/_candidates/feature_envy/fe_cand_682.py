def open_spider(self, spider: Spider):
    logger.debug(
        "Using filesystem cache storage in %(cachedir)s",
        {"cachedir": self.cachedir},
        extra={"spider": spider},
    )

    assert spider.crawler.request_fingerprinter
    self._fingerprinter = spider.crawler.request_fingerprinter
