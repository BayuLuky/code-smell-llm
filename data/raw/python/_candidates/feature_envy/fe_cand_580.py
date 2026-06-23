def _requests_to_follow(self, response):
    if not isinstance(response, HtmlResponse):
        return
    seen = set()
    for rule_index, rule in enumerate(self._rules):
        links = [
            lnk
            for lnk in rule.link_extractor.extract_links(response)
            if lnk not in seen
        ]
        for link in rule.process_links(links):
            seen.add(link)
            request = self._build_request(rule_index, link)
            yield rule.process_request(request, response)
