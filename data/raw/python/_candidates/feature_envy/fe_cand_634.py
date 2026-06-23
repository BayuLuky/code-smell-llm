def convert_value(self, value, expression, connection):
    if isinstance(self.output_field, DateTimeField):
        if not settings.USE_TZ:
            pass
        elif value is not None:
            value = value.replace(tzinfo=None)
            value = timezone.make_aware(value, self.tzinfo, is_dst=self.is_dst)
        elif not connection.features.has_zoneinfo_database:
            raise ValueError(
                "Database returned an invalid datetime value. Are time "
                "zone definitions for your database installed?"
            )
    elif isinstance(value, datetime):
        if value is None:
            pass
        elif isinstance(self.output_field, DateField):
            value = value.date()
        elif isinstance(self.output_field, TimeField):
            value = value.time()
    return value
