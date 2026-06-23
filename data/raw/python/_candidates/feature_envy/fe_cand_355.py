def from_crawler(cls, crawler):
    o = cls(crawler.stats)
    crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
    return o
