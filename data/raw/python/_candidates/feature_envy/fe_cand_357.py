def from_crawler(cls, crawler: "Crawler", *args: Any, **kwargs: Any) -> "Self":
    spider = super().from_crawler(crawler, *args, **kwargs)
    spider._max_size = getattr(
        spider, "download_maxsize", spider.settings.getint("DOWNLOAD_MAXSIZE")
    )
    spider._warn_size = getattr(
        spider, "download_warnsize", spider.settings.getint("DOWNLOAD_WARNSIZE")
    )
    return spider
