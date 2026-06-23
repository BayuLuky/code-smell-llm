def serialize(self):
    enum_class = self.value.__class__
    module = enum_class.__module__
    if issubclass(enum_class, enum.Flag):
        if PY311:
            members = list(self.value)
        else:
            members, _ = enum._decompose(enum_class, self.value)
            members = reversed(members)
    else:
        members = (self.value,)
    return (
        " | ".join(
            [
                f"{module}.{enum_class.__qualname__}[{item.name!r}]"
                for item in members
            ]
        ),
        {"import %s" % module},
    )
