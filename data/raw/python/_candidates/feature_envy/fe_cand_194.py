def _set_conditional_validators(self, request, cachedresponse):
    if b"Last-Modified" in cachedresponse.headers:
        request.headers[b"If-Modified-Since"] = cachedresponse.headers[
            b"Last-Modified"
        ]

    if b"ETag" in cachedresponse.headers:
        request.headers[b"If-None-Match"] = cachedresponse.headers[b"ETag"]
