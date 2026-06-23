def to_info_dict(self) -> t.Dict[str, t.Any]:
    """Gather information that could be useful for a tool generating
    user-facing documentation.

    Use :meth:`click.Context.to_info_dict` to traverse the entire
    CLI structure.

    .. versionadded:: 8.0
    """
    # The class name without the "ParamType" suffix.
    param_type = type(self).__name__.partition("ParamType")[0]
    param_type = param_type.partition("ParameterType")[0]

    # Custom subclasses might not remember to set a name.
    if hasattr(self, "name"):
        name = self.name
    else:
        name = param_type

    return {"param_type": param_type, "name": name}
