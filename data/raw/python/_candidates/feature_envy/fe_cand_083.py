def convert(
    self, value: t.Any, param: t.Optional["Parameter"], ctx: t.Optional["Context"]
) -> t.Any:
    if isinstance(value, bytes):
        enc = _get_argv_encoding()
        try:
            value = value.decode(enc)
        except UnicodeError:
            fs_enc = sys.getfilesystemencoding()
            if fs_enc != enc:
                try:
                    value = value.decode(fs_enc)
                except UnicodeError:
                    value = value.decode("utf-8", "replace")
            else:
                value = value.decode("utf-8", "replace")
        return value
    return str(value)
