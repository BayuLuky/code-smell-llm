def __init__(
    self,
    url: str,
    status=200,
    headers=None,
    body=b"",
    flags=None,
    request=None,
    certificate=None,
    ip_address=None,
    protocol=None,
):
    self.headers = Headers(headers or {})
    self.status = int(status)
    self._set_body(body)
    self._set_url(url)
    self.request = request
    self.flags = [] if flags is None else list(flags)
    self.certificate = certificate
    self.ip_address = ip_address
    self.protocol = protocol
