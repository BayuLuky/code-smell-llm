def from_crawler(cls, crawler):
    o = cls(crawler.settings.getfloat("DOWNLOAD_TIMEOUT"))
    crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
    return o
