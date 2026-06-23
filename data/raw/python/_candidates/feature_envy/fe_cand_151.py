def convert(
    self, value: t.Any, param: t.Optional["Parameter"], ctx: t.Optional["Context"]
) -> t.Any:
    # Match through normalization and case sensitivity
    # first do token_normalize_func, then lowercase
    # preserve original `value` to produce an accurate message in
    # `self.fail`
    normed_value = value
    normed_choices = {choice: choice for choice in self.choices}

    if ctx is not None and ctx.token_normalize_func is not None:
        normed_value = ctx.token_normalize_func(value)
        normed_choices = {
            ctx.token_normalize_func(normed_choice): original
            for normed_choice, original in normed_choices.items()
        }

    if not self.case_sensitive:
        normed_value = normed_value.casefold()
        normed_choices = {
            normed_choice.casefold(): original
            for normed_choice, original in normed_choices.items()
        }

    if normed_value in normed_choices:
        return normed_choices[normed_value]

    choices_str = ", ".join(map(repr, self.choices))
    self.fail(
        ngettext(
            "{value!r} is not {choice}.",
            "{value!r} is not one of {choices}.",
            len(self.choices),
        ).format(value=value, choice=choices_str, choices=choices_str),
        param,
        ctx,
    )
