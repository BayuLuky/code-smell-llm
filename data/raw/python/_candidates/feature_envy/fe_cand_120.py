def from_crawler(cls, crawler):
    interval = crawler.settings.getfloat("LOGSTATS_INTERVAL")
    if not interval:
        raise NotConfigured
    o = cls(crawler.stats, interval)
    crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
    crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
    return o
