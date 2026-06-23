def _parse_decls(
    self, decls: t.Sequence[str], expose_value: bool
) -> t.Tuple[t.Optional[str], t.List[str], t.List[str]]:
    if not decls:
        if not expose_value:
            return None, [], []
        raise TypeError("Could not determine name for argument")
    if len(decls) == 1:
        name = arg = decls[0]
        name = name.replace("-", "_").lower()
    else:
        raise TypeError(
            "Arguments take exactly one parameter declaration, got"
            f" {len(decls)}."
        )
    return name, [arg], []
