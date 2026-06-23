def to_json(self, value: t.Any) -> t.Any:
    # JSON objects may only have string keys, so don't bother tagging the
    # key here.
    return {k: self.serializer.tag(v) for k, v in value.items()}
