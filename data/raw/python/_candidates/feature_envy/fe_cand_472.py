def from_settings(cls, settings):
    return cls(
        smtphost=settings["MAIL_HOST"],
        mailfrom=settings["MAIL_FROM"],
        smtpuser=settings["MAIL_USER"],
        smtppass=settings["MAIL_PASS"],
        smtpport=settings.getint("MAIL_PORT"),
        smtptls=settings.getbool("MAIL_TLS"),
        smtpssl=settings.getbool("MAIL_SSL"),
    )
