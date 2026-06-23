def _redirect(self, redirected, request, spider, reason):
    ttl = request.meta.setdefault("redirect_ttl", self.max_redirect_times)
    redirects = request.meta.get("redirect_times", 0) + 1

    if ttl and redirects <= self.max_redirect_times:
        redirected.meta["redirect_times"] = redirects
        redirected.meta["redirect_ttl"] = ttl - 1
        redirected.meta["redirect_urls"] = request.meta.get("redirect_urls", []) + [
            request.url
        ]
        redirected.meta["redirect_reasons"] = request.meta.get(
            "redirect_reasons", []
        ) + [reason]
        redirected.dont_filter = request.dont_filter
        redirected.priority = request.priority + self.priority_adjust
        logger.debug(
            "Redirecting (%(reason)s) to %(redirected)s from %(request)s",
            {"reason": reason, "redirected": redirected, "request": request},
            extra={"spider": spider},
        )
        return redirected
    logger.debug(
        "Discarding %(request)s: max redirections reached",
        {"request": request},
        extra={"spider": spider},
    )
    raise IgnoreRequest("max redirections reached")
