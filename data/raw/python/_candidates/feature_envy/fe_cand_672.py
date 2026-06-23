def run(self, args: List[str], opts: Namespace) -> None:
    if len(args) != 1 or not is_url(args[0]):
        raise UsageError()
    request = Request(
        args[0],
        callback=self._print_response,
        cb_kwargs={"opts": opts},
        dont_filter=True,
    )
    # by default, let the framework handle redirects,
    # i.e. command handles all codes expect 3xx
    if not opts.no_redirect:
        request.meta["handle_httpstatus_list"] = SequenceExclude(range(300, 400))
    else:
        request.meta["handle_httpstatus_all"] = True

    spidercls: Type[Spider] = DefaultSpider
    assert self.crawler_process
    spider_loader = self.crawler_process.spider_loader
    if opts.spider:
        spidercls = spider_loader.load(opts.spider)
    else:
        spidercls = spidercls_for_request(spider_loader, request, spidercls)
    self.crawler_process.crawl(spidercls, start_requests=lambda: [request])
    self.crawler_process.start()
