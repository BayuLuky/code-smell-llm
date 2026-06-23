def _print_response(self, response, opts):
    if opts.headers:
        self._print_headers(response.request.headers, b">")
        print(">")
        self._print_headers(response.headers, b"<")
    else:
        self._print_bytes(response.body)
