def process_response(self, request, response, spider):
    self.stats.inc_value("downloader/response_count", spider=spider)
    self.stats.inc_value(
        f"downloader/response_status_count/{response.status}", spider=spider
    )
    reslen = (
        len(response.body)
        + get_header_size(response.headers)
        + get_status_size(response.status)
        + 4
    )
    # response.body + b"\r\n"+ response.header + b"\r\n" + response.status
    self.stats.inc_value("downloader/response_bytes", reslen, spider=spider)
    return response
