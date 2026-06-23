def from_crawler(cls, crawler):
    settings = crawler.settings
    maxdepth = settings.getint("DEPTH_LIMIT")
    verbose = settings.getbool("DEPTH_STATS_VERBOSE")
    prio = settings.getint("DEPTH_PRIORITY")
    return cls(maxdepth, crawler.stats, verbose, prio)
