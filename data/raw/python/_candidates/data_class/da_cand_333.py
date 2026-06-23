class DeprecatedConvertValueMixin:
    def __init__(self, *expressions, default=NOT_PROVIDED, **extra):
        if default is NOT_PROVIDED:
            default = None
            self._default_provided = False
        else:
            self._default_provided = True
        super().__init__(*expressions, default=default, **extra)

    def resolve_expression(self, *args, **kwargs):
        resolved = super().resolve_expression(*args, **kwargs)
        if not self._default_provided:
            resolved.empty_result_set_value = getattr(
                self, "deprecation_empty_result_set_value", self.deprecation_value
            )
        return resolved

    def convert_value(self, value, expression, connection):
        if value is None and not self._default_provided:
            warnings.warn(self.deprecation_msg, category=RemovedInDjango50Warning)
            return self.deprecation_value
        return value
