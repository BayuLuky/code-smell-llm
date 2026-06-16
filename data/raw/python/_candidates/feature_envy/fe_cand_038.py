def run(self, args, opts):
    # load contracts
    contracts = build_component_list(self.settings.getwithbase("SPIDER_CONTRACTS"))
    conman = ContractsManager(load_object(c) for c in contracts)
    runner = TextTestRunner(verbosity=2 if opts.verbose else 1)
    result = TextTestResult(runner.stream, runner.descriptions, runner.verbosity)

    # contract requests
    contract_reqs = defaultdict(list)

    spider_loader = self.crawler_process.spider_loader

    with set_environ(SCRAPY_CHECK="true"):
        for spidername in args or spider_loader.list():
            spidercls = spider_loader.load(spidername)
            spidercls.start_requests = lambda s: conman.from_spider(s, result)

            tested_methods = conman.tested_methods_from_spidercls(spidercls)
            if opts.list:
                for method in tested_methods:
                    contract_reqs[spidercls.name].append(method)
            elif tested_methods:
                self.crawler_process.crawl(spidercls)

        # start checks
        if opts.list:
            for spider, methods in sorted(contract_reqs.items()):
                if not methods and not opts.verbose:
                    continue
                print(spider)
                for method in sorted(methods):
                    print(f"  * {method}")
        else:
            start = time.time()
            self.crawler_process.start()
            stop = time.time()

            result.printErrors()
            result.printSummary(start, stop)
            self.exitcode = int(not result.wasSuccessful())
