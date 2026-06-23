def _get_sitemap_body(self, response):
    """Return the sitemap body contained in the given response,
    or None if the response is not a sitemap.
    """
    if isinstance(response, XmlResponse):
        return response.body
    if gzip_magic_number(response):
        uncompressed_size = len(response.body)
        max_size = response.meta.get("download_maxsize", self._max_size)
        warn_size = response.meta.get("download_warnsize", self._warn_size)
        try:
            body = gunzip(response.body, max_size=max_size)
        except _DecompressionMaxSizeExceeded:
            return None
        if uncompressed_size < warn_size <= len(body):
            logger.warning(
                f"{response} body size after decompression ({len(body)} B) "
                f"is larger than the download warning size ({warn_size} B)."
            )
        return body
    # actual gzipped sitemap files are decompressed above ;
    # if we are here (response body is not gzipped)
    # and have a response for .xml.gz,
    # it usually means that it was already gunzipped
    # by HttpCompression middleware,
    # the HTTP response being sent with "Content-Encoding: gzip"
    # without actually being a .xml.gz file in the first place,
    # merely XML gzip-compressed on the fly,
    # in other word, here, we have plain XML
    if response.url.endswith(".xml") or response.url.endswith(".xml.gz"):
        return response.body
