def _unique_sql(
    self,
    model,
    fields,
    name,
    condition=None,
    deferrable=None,
    include=None,
    opclasses=None,
    expressions=None,
):
    if (
        deferrable
        and not self.connection.features.supports_deferrable_unique_constraints
    ):
        return None
    if condition or include or opclasses or expressions:
        # Databases support conditional, covering, and functional unique
        # constraints via a unique index.
        sql = self._create_unique_sql(
            model,
            fields,
            name=name,
            condition=condition,
            include=include,
            opclasses=opclasses,
            expressions=expressions,
        )
        if sql:
            self.deferred_sql.append(sql)
        return None
    constraint = self.sql_unique_constraint % {
        "columns": ", ".join([self.quote_name(field.column) for field in fields]),
        "deferrable": self._deferrable_constraint_sql(deferrable),
    }
    return self.sql_constraint % {
        "name": self.quote_name(name),
        "constraint": constraint,
    }
