def _failed(self, result, request):
    message = result.getErrorMessage()
    if result.type == CommandFailed:
        m = _CODE_RE.search(message)
        if m:
            ftpcode = m.group()
            httpcode = self.CODE_MAPPING.get(ftpcode, self.CODE_MAPPING["default"])
            return Response(
                url=request.url, status=httpcode, body=to_bytes(message)
            )
    raise result.type(result.value)
