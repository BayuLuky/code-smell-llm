def __init__(self, types: t.Sequence[t.Union[t.Type[t.Any], ParamType]]) -> None:
    self.types: t.Sequence[ParamType] = [convert_type(ty) for ty in types]
