def tag(self, value: t.Any) -> t.Any:
    """Convert a value to a tagged representation if necessary."""
    for tag in self.order:
        if tag.check(value):
            return tag.tag(value)

    return value
