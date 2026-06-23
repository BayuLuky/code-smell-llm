def __init__(self, crawler):
    self.crawler = crawler
    if not crawler.settings.getbool("AUTOTHROTTLE_ENABLED"):
        raise NotConfigured

    self.debug = crawler.settings.getbool("AUTOTHROTTLE_DEBUG")
    self.target_concurrency = crawler.settings.getfloat(
        "AUTOTHROTTLE_TARGET_CONCURRENCY"
    )
    crawler.signals.connect(self._spider_opened, signal=signals.spider_opened)
    crawler.signals.connect(
        self._response_downloaded, signal=signals.response_downloaded
    )
