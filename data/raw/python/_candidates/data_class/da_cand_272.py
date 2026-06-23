class StrictOriginPolicy(ReferrerPolicy):
    """
    https://www.w3.org/TR/referrer-policy/#referrer-policy-strict-origin

    The "strict-origin" policy sends the ASCII serialization
    of the origin of the request client when making requests:
    - from a TLS-protected environment settings object to a potentially trustworthy URL, and
    - from non-TLS-protected environment settings objects to any origin.

    Requests from TLS-protected request clients to non- potentially trustworthy URLs,
    on the other hand, will contain no referrer information.
    A Referer HTTP header will not be sent.
    """

    name: str = POLICY_STRICT_ORIGIN

    def referrer(self, response_url, request_url):
        if (
            self.tls_protected(response_url)
            and self.potentially_trustworthy(request_url)
            or not self.tls_protected(response_url)
        ):
            return self.origin_referrer(response_url)
