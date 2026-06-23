def _copytree(self, src: Path, dst: Path):
    """
    Since the original function always creates the directory, to resolve
    the issue a new function had to be created. It's a simple copy and
    was reduced for this case.

    More info at:
    https://github.com/scrapy/scrapy/pull/2005
    """
    ignore = IGNORE
    names = [x.name for x in src.iterdir()]
    ignored_names = ignore(src, names)

    if not dst.exists():
        dst.mkdir(parents=True)

    for name in names:
        if name in ignored_names:
            continue

        srcname = src / name
        dstname = dst / name
        if srcname.is_dir():
            self._copytree(srcname, dstname)
        else:
            copy2(srcname, dstname)
            _make_writable(dstname)

    copystat(src, dst)
    _make_writable(dst)
