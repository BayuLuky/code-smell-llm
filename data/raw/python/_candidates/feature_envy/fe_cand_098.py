def from_crawler(
    cls: Type[HttpCacheMiddlewareTV], crawler: Crawler
) -> HttpCacheMiddlewareTV:
    assert crawler.stats
    o = cls(crawler.settings, crawler.stats)
    crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
    crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
    return o
