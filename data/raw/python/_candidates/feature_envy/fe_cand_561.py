def _connect(self, factory):
    from twisted.internet import reactor

    host, port = to_unicode(factory.host), factory.port
    if factory.scheme == b"https":
        client_context_factory = create_instance(
            objcls=self.ClientContextFactory,
            settings=self._settings,
            crawler=self._crawler,
        )
        return reactor.connectSSL(host, port, factory, client_context_factory)
    return reactor.connectTCP(host, port, factory)
