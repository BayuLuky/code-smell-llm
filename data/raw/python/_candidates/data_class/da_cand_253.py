class Regex(BuiltinLookup):
    lookup_name = "regex"
    prepare_rhs = False

    def as_sql(self, compiler, connection):
        if self.lookup_name in connection.operators:
            return super().as_sql(compiler, connection)
        else:
            lhs, lhs_params = self.process_lhs(compiler, connection)
            rhs, rhs_params = self.process_rhs(compiler, connection)
            sql_template = connection.ops.regex_lookup(self.lookup_name)
            return sql_template % (lhs, rhs), lhs_params + rhs_params
