def stat_file(self, path: Union[str, PathLike], info):
    absolute_path = self._get_filesystem_path(path)
    try:
        last_modified = absolute_path.stat().st_mtime
    except os.error:
        return {}

    with absolute_path.open("rb") as f:
        checksum = md5sum(f)

    return {"last_modified": last_modified, "checksum": checksum}
