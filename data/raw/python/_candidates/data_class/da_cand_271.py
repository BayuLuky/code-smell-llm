class Portal:
    """An implementation of IPortal"""

    @defers
    def login(self_, credentials, mind, *interfaces):
        if not (
            credentials.username == self.username.encode("utf8")
            and credentials.checkPassword(self.password.encode("utf8"))
        ):
            raise ValueError("Invalid credentials")

        protocol = telnet.TelnetBootstrapProtocol(
            insults.ServerProtocol, manhole.Manhole, self._get_telnet_vars()
        )
        return (interfaces[0], protocol, lambda: None)
