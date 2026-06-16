class DateFieldListFilter(FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.field_generic = "%s__" % field_path
        self.date_params = {
            k: v for k, v in params.items() if k.startswith(self.field_generic)
        }

        now = timezone.now()
        # When time zone support is enabled, convert "now" to the user's time
        # zone so Django's definition of "Today" matches what the user expects.
        if timezone.is_aware(now):
            now = timezone.localtime(now)

        if isinstance(field, models.DateTimeField):
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:  # field is a models.DateField
            today = now.date()
        tomorrow = today + datetime.timedelta(days=1)
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
        next_year = today.replace(year=today.year + 1, month=1, day=1)

        self.lookup_kwarg_since = "%s__gte" % field_path
        self.lookup_kwarg_until = "%s__lt" % field_path
        self.links = (
            (_("Any date"), {}),
            (
                _("Today"),
                {
                    self.lookup_kwarg_since: str(today),
                    self.lookup_kwarg_until: str(tomorrow),
                },
            ),
            (
                _("Past 7 days"),
                {
                    self.lookup_kwarg_since: str(today - datetime.timedelta(days=7)),
                    self.lookup_kwarg_until: str(tomorrow),
                },
            ),
            (
                _("This month"),
                {
                    self.lookup_kwarg_since: str(today.replace(day=1)),
                    self.lookup_kwarg_until: str(next_month),
                },
            ),
            (
                _("This year"),
                {
                    self.lookup_kwarg_since: str(today.replace(month=1, day=1)),
                    self.lookup_kwarg_until: str(next_year),
                },
            ),
        )
        if field.null:
            self.lookup_kwarg_isnull = "%s__isnull" % field_path
            self.links += (
                (_("No date"), {self.field_generic + "isnull": "True"}),
                (_("Has date"), {self.field_generic + "isnull": "False"}),
            )
        super().__init__(field, request, params, model, model_admin, field_path)

    def expected_parameters(self):
        params = [self.lookup_kwarg_since, self.lookup_kwarg_until]
        if self.field.null:
            params.append(self.lookup_kwarg_isnull)
        return params

    def choices(self, changelist):
        for title, param_dict in self.links:
            yield {
                "selected": self.date_params == param_dict,
                "query_string": changelist.get_query_string(
                    param_dict, [self.field_generic]
                ),
                "display": title,
            }
