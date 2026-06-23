class Exact(FieldGetDbPrepValueMixin, BuiltinLookup):
    lookup_name = "exact"

    def get_prep_lookup(self):
        from django.db.models.sql.query import Query  # avoid circular import

        if isinstance(self.rhs, Query):
            if self.rhs.has_limit_one():
                if not self.rhs.has_select_fields:
                    self.rhs.clear_select_clause()
                    self.rhs.add_fields(["pk"])
            else:
                raise ValueError(
                    "The QuerySet value for an exact lookup must be limited to "
                    "one result using slicing."
                )
        return super().get_prep_lookup()

    def as_sql(self, compiler, connection):
        # Avoid comparison against direct rhs if lhs is a boolean value. That
        # turns "boolfield__exact=True" into "WHERE boolean_field" instead of
        # "WHERE boolean_field = True" when allowed.
        if (
            isinstance(self.rhs, bool)
            and getattr(self.lhs, "conditional", False)
            and connection.ops.conditional_expression_supported_in_where_clause(
                self.lhs
            )
        ):
            lhs_sql, params = self.process_lhs(compiler, connection)
            template = "%s" if self.rhs else "NOT %s"
            return template % lhs_sql, params
        return super().as_sql(compiler, connection)
