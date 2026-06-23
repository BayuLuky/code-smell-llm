class Extract(TimezoneMixin, Transform):
    lookup_name = None
    output_field = IntegerField()

    def __init__(self, expression, lookup_name=None, tzinfo=None, **extra):
        if self.lookup_name is None:
            self.lookup_name = lookup_name
        if self.lookup_name is None:
            raise ValueError("lookup_name must be provided")
        self.tzinfo = tzinfo
        super().__init__(expression, **extra)

    def as_sql(self, compiler, connection):
        sql, params = compiler.compile(self.lhs)
        lhs_output_field = self.lhs.output_field
        if isinstance(lhs_output_field, DateTimeField):
            tzname = self.get_tzname()
            sql, params = connection.ops.datetime_extract_sql(
                self.lookup_name, sql, tuple(params), tzname
            )
        elif self.tzinfo is not None:
            raise ValueError("tzinfo can only be used with DateTimeField.")
        elif isinstance(lhs_output_field, DateField):
            sql, params = connection.ops.date_extract_sql(
                self.lookup_name, sql, tuple(params)
            )
        elif isinstance(lhs_output_field, TimeField):
            sql, params = connection.ops.time_extract_sql(
                self.lookup_name, sql, tuple(params)
            )
        elif isinstance(lhs_output_field, DurationField):
            if not connection.features.has_native_duration_field:
                raise ValueError(
                    "Extract requires native DurationField database support."
                )
            sql, params = connection.ops.time_extract_sql(
                self.lookup_name, sql, tuple(params)
            )
        else:
            # resolve_expression has already validated the output_field so this
            # assert should never be hit.
            assert False, "Tried to Extract from an invalid type."
        return sql, params

    def resolve_expression(
        self, query=None, allow_joins=True, reuse=None, summarize=False, for_save=False
    ):
        copy = super().resolve_expression(
            query, allow_joins, reuse, summarize, for_save
        )
        field = getattr(copy.lhs, "output_field", None)
        if field is None:
            return copy
        if not isinstance(field, (DateField, DateTimeField, TimeField, DurationField)):
            raise ValueError(
                "Extract input expression must be DateField, DateTimeField, "
                "TimeField, or DurationField."
            )
        # Passing dates to functions expecting datetimes is most likely a mistake.
        if type(field) is DateField and copy.lookup_name in (
            "hour",
            "minute",
            "second",
        ):
            raise ValueError(
                "Cannot extract time component '%s' from DateField '%s'."
                % (copy.lookup_name, field.name)
            )
        if isinstance(field, DurationField) and copy.lookup_name in (
            "year",
            "iso_year",
            "month",
            "week",
            "week_day",
            "iso_week_day",
            "quarter",
        ):
            raise ValueError(
                "Cannot extract component '%s' from DurationField '%s'."
                % (copy.lookup_name, field.name)
            )
        return copy
