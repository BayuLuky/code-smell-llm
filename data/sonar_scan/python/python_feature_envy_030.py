def from_crawler(cls, crawler):
    if not crawler.settings.getbool("COMPRESSION_ENABLED"):
        raise NotConfigured
    try:
        return cls(crawler=crawler)
    except TypeError:
        warnings.warn(
            "HttpCompressionMiddleware subclasses must either modify "
            "their '__init__' method to support a 'crawler' parameter or "
            "reimplement their 'from_crawler' method.",
            ScrapyDeprecationWarning,
        )
        mw = cls()
        mw.stats = crawler.stats
        mw._max_size = crawler.settings.getint("DOWNLOAD_MAXSIZE")
        mw._warn_size = crawler.settings.getint("DOWNLOAD_WARNSIZE")
        crawler.signals.connect(mw.open_spider, signals.spider_opened)
        return mw
