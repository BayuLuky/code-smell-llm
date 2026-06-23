def request(self, request: Request, spider: Spider) -> Deferred:
    uri = URI.fromBytes(bytes(request.url, encoding="utf-8"))
    try:
        endpoint = self.get_endpoint(uri)
    except SchemeNotSupported:
        return defer.fail(Failure())

    key = self.get_key(uri)
    d = self._pool.get_connection(key, uri, endpoint)
    d.addCallback(lambda conn: conn.request(request, spider))
    return d
