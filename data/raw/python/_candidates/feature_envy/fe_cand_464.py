def download_request(self, request, spider):
    filepath = file_uri_to_path(request.url)
    body = Path(filepath).read_bytes()
    respcls = responsetypes.from_args(filename=filepath, body=body)
    return respcls(url=request.url, body=body)
