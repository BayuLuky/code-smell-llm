def from_crawler(cls, crawler):
    o = cls(crawler.settings["USER_AGENT"])
    crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
    return o
