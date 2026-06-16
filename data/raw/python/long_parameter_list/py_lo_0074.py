def __init__(
    self,
    smtphost="localhost",
    mailfrom="scrapy@localhost",
    smtpuser=None,
    smtppass=None,
    smtpport=25,
    smtptls=False,
    smtpssl=False,
    debug=False,
):
    self.smtphost = smtphost
    self.smtpport = smtpport
    self.smtpuser = _to_bytes_or_none(smtpuser)
    self.smtppass = _to_bytes_or_none(smtppass)
    self.smtptls = smtptls
    self.smtpssl = smtpssl
    self.mailfrom = mailfrom
    self.debug = debug
