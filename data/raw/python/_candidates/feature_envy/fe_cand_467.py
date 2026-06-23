def get_key(self, uri: URI) -> Tuple:
    """
    Arguments:
        uri - URI obtained directly from request URL
    """
    return uri.scheme, uri.host, uri.port
