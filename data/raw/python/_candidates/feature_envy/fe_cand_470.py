def _compute_current_age(self, response, request, now):
    # Reference nsHttpResponseHead::ComputeCurrentAge
    # https://dxr.mozilla.org/mozilla-central/source/netwerk/protocol/http/nsHttpResponseHead.cpp#658
    currentage = 0
    # If Date header is not set we assume it is a fast connection, and
    # clock is in sync with the server
    date = rfc1123_to_epoch(response.headers.get(b"Date")) or now
    if now > date:
        currentage = now - date

    if b"Age" in response.headers:
        try:
            age = int(response.headers[b"Age"])
            currentage = max(currentage, age)
        except ValueError:
            pass

    return currentage
