def edit_file(self, filename: str) -> None:
    import subprocess

    editor = self.get_editor()
    environ: t.Optional[t.Dict[str, str]] = None

    if self.env:
        environ = os.environ.copy()
        environ.update(self.env)

    try:
        c = subprocess.Popen(f'{editor} "{filename}"', env=environ, shell=True)
        exit_code = c.wait()
        if exit_code != 0:
            raise ClickException(
                _("{editor}: Editing failed").format(editor=editor)
            )
    except OSError as e:
        raise ClickException(
            _("{editor}: Editing failed: {e}").format(editor=editor, e=e)
        ) from e
