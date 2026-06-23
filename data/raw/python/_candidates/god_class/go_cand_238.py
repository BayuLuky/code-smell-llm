class JSONField(CheckFieldDefaultMixin, Field):
    empty_strings_allowed = False
    description = _("A JSON object")
    default_error_messages = {
        "invalid": _("Value must be valid JSON."),
    }
    _default_hint = ("dict", "{}")

    def __init__(
        self,
        verbose_name=None,
        name=None,
        encoder=None,
        decoder=None,
        **kwargs,
    ):
        if encoder and not callable(encoder):
            raise ValueError("The encoder parameter must be a callable object.")
        if decoder and not callable(decoder):
            raise ValueError("The decoder parameter must be a callable object.")
        self.encoder = encoder
        self.decoder = decoder
        super().__init__(verbose_name, name, **kwargs)

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        databases = kwargs.get("databases") or []
        errors.extend(self._check_supported(databases))
        return errors

    def _check_supported(self, databases):
        errors = []
        for db in databases:
            if not router.allow_migrate_model(db, self.model):
                continue
            connection = connections[db]
            if (
                self.model._meta.required_db_vendor
                and self.model._meta.required_db_vendor != connection.vendor
            ):
                continue
            if not (
                "supports_json_field" in self.model._meta.required_db_features
                or connection.features.supports_json_field
            ):
                errors.append(
                    checks.Error(
                        "%s does not support JSONFields." % connection.display_name,
                        obj=self.model,
                        id="fields.E180",
                    )
                )
        return errors

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.encoder is not None:
            kwargs["encoder"] = self.encoder
        if self.decoder is not None:
            kwargs["decoder"] = self.decoder
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        # Some backends (SQLite at least) extract non-string values in their
        # SQL datatypes.
        if isinstance(expression, KeyTransform) and not isinstance(value, str):
            return value
        try:
            return json.loads(value, cls=self.decoder)
        except json.JSONDecodeError:
            return value

    def get_internal_type(self):
        return "JSONField"

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)
        # RemovedInDjango51Warning: When the deprecation ends, replace with:
        # if (
        #     isinstance(value, expressions.Value)
        #     and isinstance(value.output_field, JSONField)
        # ):
        #     value = value.value
        # elif hasattr(value, "as_sql"): ...
        if isinstance(value, expressions.Value):
            if isinstance(value.value, str) and not isinstance(
                value.output_field, JSONField
            ):
                try:
                    value = json.loads(value.value, cls=self.decoder)
                except json.JSONDecodeError:
                    value = value.value
                else:
                    warnings.warn(
                        "Providing an encoded JSON string via Value() is deprecated. "
                        f"Use Value({value!r}, output_field=JSONField()) instead.",
                        category=RemovedInDjango51Warning,
                    )
            elif isinstance(value.output_field, JSONField):
                value = value.value
            else:
                return value
        elif hasattr(value, "as_sql"):
            return value
        return connection.ops.adapt_json_value(value, self.encoder)

    def get_db_prep_save(self, value, connection):
        if value is None:
            return value
        return self.get_db_prep_value(value, connection)

    def get_transform(self, name):
        transform = super().get_transform(name)
        if transform:
            return transform
        return KeyTransformFactory(name)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        try:
            json.dumps(value, cls=self.encoder)
        except TypeError:
            raise exceptions.ValidationError(
                self.error_messages["invalid"],
                code="invalid",
                params={"value": value},
            )

    def value_to_string(self, obj):
        return self.value_from_object(obj)

    def formfield(self, **kwargs):
        return super().formfield(
            **{
                "form_class": forms.JSONField,
                "encoder": self.encoder,
                "decoder": self.decoder,
                **kwargs,
            }
        )
