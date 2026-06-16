def __init__(
    self,
    exists: bool = False,
    file_okay: bool = True,
    dir_okay: bool = True,
    writable: bool = False,
    readable: bool = True,
    resolve_path: bool = False,
    allow_dash: bool = False,
    path_type: t.Optional[t.Type[t.Any]] = None,
    executable: bool = False,
):
    self.exists = exists
    self.file_okay = file_okay
    self.dir_okay = dir_okay
    self.readable = readable
    self.writable = writable
    self.executable = executable
    self.resolve_path = resolve_path
    self.allow_dash = allow_dash
    self.type = path_type

    if self.file_okay and not self.dir_okay:
        self.name: str = _("file")
    elif self.dir_okay and not self.file_okay:
        self.name = _("directory")
    else:
        self.name = _("path")
