class MetaRefreshMiddleware(BaseRedirectMiddleware):
    enabled_setting = "METAREFRESH_ENABLED"

    def __init__(self, settings):
        super().__init__(settings)
        self._ignore_tags = settings.getlist("METAREFRESH_IGNORE_TAGS")
        self._maxdelay = settings.getint("METAREFRESH_MAXDELAY")

    def process_response(self, request, response, spider):
        if (
            request.meta.get("dont_redirect", False)
            or request.method == "HEAD"
            or not isinstance(response, HtmlResponse)
            or urlparse_cached(request).scheme not in {"http", "https"}
        ):
            return response

        interval, url = get_meta_refresh(response, ignore_tags=self._ignore_tags)
        if not url:
            return response
        if urlparse(url).scheme not in {"http", "https"}:
            return response
        if interval < self._maxdelay:
            redirected = self._redirect_request_using_get(request, url)
            return self._redirect(redirected, request, spider, "meta refresh")
        return response
