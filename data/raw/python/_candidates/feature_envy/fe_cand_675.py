def start(
    self, stop_after_crawl: bool = True, install_signal_handlers: bool = True
) -> None:
    """
    This method starts a :mod:`~twisted.internet.reactor`, adjusts its pool
    size to :setting:`REACTOR_THREADPOOL_MAXSIZE`, and installs a DNS cache
    based on :setting:`DNSCACHE_ENABLED` and :setting:`DNSCACHE_SIZE`.

    If ``stop_after_crawl`` is True, the reactor will be stopped after all
    crawlers have finished, using :meth:`join`.

    :param bool stop_after_crawl: stop or not the reactor when all
        crawlers have finished

    :param bool install_signal_handlers: whether to install the OS signal
        handlers from Twisted and Scrapy (default: True)
    """
    from twisted.internet import reactor

    if stop_after_crawl:
        d = self.join()
        # Don't start the reactor if the deferreds are already fired
        if d.called:
            return
        d.addBoth(self._stop_reactor)

    resolver_class = load_object(self.settings["DNS_RESOLVER"])
    resolver = create_instance(resolver_class, self.settings, self, reactor=reactor)
    resolver.install_on_reactor()
    tp = reactor.getThreadPool()
    tp.adjustPoolsize(maxthreads=self.settings.getint("REACTOR_THREADPOOL_MAXSIZE"))
    reactor.addSystemEventTrigger("before", "shutdown", self.stop)
    if install_signal_handlers:
        reactor.addSystemEventTrigger(
            "after", "startup", install_shutdown_handlers, self._signal_shutdown
        )
    reactor.run(installSignalHandlers=install_signal_handlers)  # blocking call
