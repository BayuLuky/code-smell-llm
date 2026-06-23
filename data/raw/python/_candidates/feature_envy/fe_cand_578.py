def _set_referer(self, r, response):
    if isinstance(r, Request):
        referrer = self.policy(response, r).referrer(response.url, r.url)
        if referrer is not None:
            r.headers.setdefault("Referer", referrer)
    return r
