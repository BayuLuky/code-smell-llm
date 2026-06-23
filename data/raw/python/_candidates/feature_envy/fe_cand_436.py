def to_json(self, value: t.Any) -> t.Any:
    return str(value.__html__())
