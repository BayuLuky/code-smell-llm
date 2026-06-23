def __init__(self, *expressions, default=NOT_PROVIDED, **extra):
    super().__init__(*expressions, default=default, **extra)
    if (
        isinstance(default, Value)
        and isinstance(default.value, str)
        and not isinstance(default.output_field, JSONField)
    ):
        value = default.value
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            warnings.warn(
                "Passing a Value() with an output_field that isn't a JSONField as "
                "JSONBAgg(default) is deprecated. Pass default="
                f"Value({value!r}, output_field=JSONField()) instead.",
                stacklevel=2,
                category=RemovedInDjango51Warning,
            )
            self.default.output_field = self.output_field
        else:
            self.default = Value(decoded, self.output_field)
            warnings.warn(
                "Passing an encoded JSON string as JSONBAgg(default) is "
                f"deprecated. Pass default={decoded!r} instead.",
                stacklevel=2,
                category=RemovedInDjango51Warning,
            )
