def extract_links(self, response):
    base_url = get_base_url(response)
    return self._extract_links(
        response.selector, response.url, response.encoding, base_url
    )
