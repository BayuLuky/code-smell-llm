def render(self, request):
    total = _getarg(request, b"total", 100, int)
    show = _getarg(request, b"show", 10, int)
    nlist = [random.randint(1, total) for _ in range(show)]
    request.write(b"<html><head></head><body>")
    args = request.args.copy()
    for nl in nlist:
        args["n"] = nl
        argstr = urlencode(args, doseq=True)
        request.write(
            f"<a href='/follow?{argstr}'>follow {nl}</a><br>".encode("utf8")
        )
    request.write(b"</body></html>")
    return b""
