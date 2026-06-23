def convert(
    self,
    value: t.Union[str, "os.PathLike[str]", t.IO[t.Any]],
    param: t.Optional["Parameter"],
    ctx: t.Optional["Context"],
) -> t.IO[t.Any]:
    if _is_file_like(value):
        return value

    value = t.cast("t.Union[str, os.PathLike[str]]", value)

    try:
        lazy = self.resolve_lazy_flag(value)

        if lazy:
            lf = LazyFile(
                value, self.mode, self.encoding, self.errors, atomic=self.atomic
            )

            if ctx is not None:
                ctx.call_on_close(lf.close_intelligently)

            return t.cast(t.IO[t.Any], lf)

        f, should_close = open_stream(
            value, self.mode, self.encoding, self.errors, atomic=self.atomic
        )

        # If a context is provided, we automatically close the file
        # at the end of the context execution (or flush out).  If a
        # context does not exist, it's the caller's responsibility to
        # properly close the file.  This for instance happens when the
        # type is used with prompts.
        if ctx is not None:
            if should_close:
                ctx.call_on_close(safecall(f.close))
            else:
                ctx.call_on_close(safecall(f.flush))

        return f
    except OSError as e:  # noqa: B014
        self.fail(f"'{format_filename(value)}': {e.strerror}", param, ctx)
