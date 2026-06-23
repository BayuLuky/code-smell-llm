def from_crawler(cls, crawler, reactor):
    if crawler.settings.getbool("DNSCACHE_ENABLED"):
        cache_size = crawler.settings.getint("DNSCACHE_SIZE")
    else:
        cache_size = 0
    return cls(reactor, cache_size, crawler.settings.getfloat("DNS_TIMEOUT"))
