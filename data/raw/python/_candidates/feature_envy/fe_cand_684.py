def __init__(self, crawler):
    if not crawler.settings.getbool("MEMUSAGE_ENABLED"):
        raise NotConfigured
    try:
        # stdlib's resource module is only available on unix platforms.
        self.resource = import_module("resource")
    except ImportError:
        raise NotConfigured

    self.crawler = crawler
    self.warned = False
    self.notify_mails = crawler.settings.getlist("MEMUSAGE_NOTIFY_MAIL")
    self.limit = crawler.settings.getint("MEMUSAGE_LIMIT_MB") * 1024 * 1024
    self.warning = crawler.settings.getint("MEMUSAGE_WARNING_MB") * 1024 * 1024
    self.check_interval = crawler.settings.getfloat(
        "MEMUSAGE_CHECK_INTERVAL_SECONDS"
    )
    self.mail = MailSender.from_settings(crawler.settings)
    crawler.signals.connect(self.engine_started, signal=signals.engine_started)
    crawler.signals.connect(self.engine_stopped, signal=signals.engine_stopped)
