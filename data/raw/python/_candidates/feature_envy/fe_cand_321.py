def load(self, fp: t.IO[t.AnyStr], **kwargs: t.Any) -> t.Any:
    """Deserialize data as JSON read from a file.

    :param fp: A file opened for reading text or UTF-8 bytes.
    :param kwargs: May be passed to the underlying JSON library.
    """
    return self.loads(fp.read(), **kwargs)
