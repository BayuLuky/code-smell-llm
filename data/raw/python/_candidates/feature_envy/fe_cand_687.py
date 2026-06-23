def persist_file(
    self, path: Union[str, PathLike], buf, info, meta=None, headers=None
):
    absolute_path = self._get_filesystem_path(path)
    self._mkdir(absolute_path.parent, info)
    absolute_path.write_bytes(buf.getvalue())
