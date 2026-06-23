class InvalidHostname(H2Error):
    def __init__(
        self, request: Request, expected_hostname: str, expected_netloc: str
    ) -> None:
        self.request = request
        self.expected_hostname = expected_hostname
        self.expected_netloc = expected_netloc

    def __str__(self) -> str:
        return f"InvalidHostname: Expected {self.expected_hostname} or {self.expected_netloc} in {self.request}"
