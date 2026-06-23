def __init__(self, crawler=None):
    self.crawler = crawler
    try:
        signal.signal(signal.SIGUSR2, self.dump_stacktrace)
        signal.signal(signal.SIGQUIT, self.dump_stacktrace)
    except AttributeError:
        # win32 platforms don't support SIGUSR signals
        pass
