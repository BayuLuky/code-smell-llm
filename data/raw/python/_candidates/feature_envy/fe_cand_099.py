def process_response(self, request, response, spider):
    if request.method == "HEAD":
        return response
    if isinstance(response, Response):
        content_encoding = response.headers.getlist("Content-Encoding")
        if content_encoding:
            encoding = content_encoding.pop()
            max_size = request.meta.get("download_maxsize", self._max_size)
            warn_size = request.meta.get("download_warnsize", self._warn_size)
            try:
                decoded_body = self._decode(
                    response.body, encoding.lower(), max_size
                )
            except _DecompressionMaxSizeExceeded:
                raise IgnoreRequest(
                    f"Ignored response {response} because its body "
                    f"({len(response.body)} B) exceeded DOWNLOAD_MAXSIZE "
                    f"({max_size} B) during decompression."
                )
            if len(response.body) < warn_size <= len(decoded_body):
                logger.warning(
                    f"{response} body size after decompression "
                    f"({len(decoded_body)} B) is larger than the "
                    f"download warning size ({warn_size} B)."
                )
            if self.stats:
                self.stats.inc_value(
                    "httpcompression/response_bytes",
                    len(decoded_body),
                    spider=spider,
                )
                self.stats.inc_value(
                    "httpcompression/response_count", spider=spider
                )
            respcls = responsetypes.from_args(
                headers=response.headers, url=response.url, body=decoded_body
            )
            kwargs = dict(cls=respcls, body=decoded_body)
            if issubclass(respcls, TextResponse):
                # force recalculating the encoding until we make sure the
                # responsetypes guessing is reliable
                kwargs["encoding"] = None
            response = response.replace(**kwargs)
            if not content_encoding:
                del response.headers["Content-Encoding"]

    return response
