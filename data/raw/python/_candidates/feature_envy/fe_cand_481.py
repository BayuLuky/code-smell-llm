def shell_complete(
    self, ctx: "Context", param: "Parameter", incomplete: str
) -> t.List["CompletionItem"]:
    """Complete choices that start with the incomplete value.

    :param ctx: Invocation context for this command.
    :param param: The parameter that is requesting completion.
    :param incomplete: Value being completed. May be empty.

    .. versionadded:: 8.0
    """
    from click.shell_completion import CompletionItem

    str_choices = map(str, self.choices)

    if self.case_sensitive:
        matched = (c for c in str_choices if c.startswith(incomplete))
    else:
        incomplete = incomplete.lower()
        matched = (c for c in str_choices if c.lower().startswith(incomplete))

    return [CompletionItem(c) for c in matched]
