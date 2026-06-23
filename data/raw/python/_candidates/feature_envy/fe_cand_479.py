def show(self, file: t.Optional[t.IO[t.Any]] = None) -> None:
    if file is None:
        file = get_text_stderr()

    echo(_("Error: {message}").format(message=self.format_message()), file=file)
