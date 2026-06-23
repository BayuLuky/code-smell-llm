class HttpResponseRedirectBase(HttpResponse):
    allowed_schemes = ["http", "https", "ftp"]

    def __init__(self, redirect_to, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["Location"] = iri_to_uri(redirect_to)
        parsed = urlparse(str(redirect_to))
        if parsed.scheme and parsed.scheme not in self.allowed_schemes:
            raise DisallowedRedirect(
                "Unsafe redirect to URL with protocol '%s'" % parsed.scheme
            )

    url = property(lambda self: self["Location"])

    def __repr__(self):
        return (
            '<%(cls)s status_code=%(status_code)d%(content_type)s, url="%(url)s">'
            % {
                "cls": self.__class__.__name__,
                "status_code": self.status_code,
                "content_type": self._content_type_for_repr,
                "url": self.url,
            }
        )
