def store_response(self, spider: Spider, request: Request, response):
    """Store the given response in the cache."""
    rpath = Path(self._get_request_path(spider, request))
    if not rpath.exists():
        rpath.mkdir(parents=True)
    metadata = {
        "url": request.url,
        "method": request.method,
        "status": response.status,
        "response_url": response.url,
        "timestamp": time(),
    }
    with self._open(rpath / "meta", "wb") as f:
        f.write(to_bytes(repr(metadata)))
    with self._open(rpath / "pickled_meta", "wb") as f:
        pickle.dump(metadata, f, protocol=4)
    with self._open(rpath / "response_headers", "wb") as f:
        f.write(headers_dict_to_raw(response.headers))
    with self._open(rpath / "response_body", "wb") as f:
        f.write(response.body)
    with self._open(rpath / "request_headers", "wb") as f:
        f.write(headers_dict_to_raw(request.headers))
    with self._open(rpath / "request_body", "wb") as f:
        f.write(request.body)
