def from_crawler(cls, crawler):
    jobdir = job_dir(crawler.settings)
    if not jobdir:
        raise NotConfigured

    obj = cls(jobdir)
    crawler.signals.connect(obj.spider_closed, signal=signals.spider_closed)
    crawler.signals.connect(obj.spider_opened, signal=signals.spider_opened)
    return obj
