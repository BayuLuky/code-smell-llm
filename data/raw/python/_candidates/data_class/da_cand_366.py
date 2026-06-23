class H2ClientFactory(Factory):
    def __init__(
        self, uri: URI, settings: Settings, conn_lost_deferred: Deferred
    ) -> None:
        self.uri = uri
        self.settings = settings
        self.conn_lost_deferred = conn_lost_deferred

    def buildProtocol(self, addr) -> H2ClientProtocol:
        return H2ClientProtocol(self.uri, self.settings, self.conn_lost_deferred)

    def acceptableProtocols(self) -> List[bytes]:
        return [PROTOCOL_NAME]
