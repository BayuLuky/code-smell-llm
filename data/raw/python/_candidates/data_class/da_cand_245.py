class RelateLookup(GISLookup):
    lookup_name = "relate"
    sql_template = "%(func)s(%(lhs)s, %(rhs)s, %%s)"
    pattern_regex = _lazy_re_compile(r"^[012TF\*]{9}$")

    def process_rhs(self, compiler, connection):
        # Check the pattern argument
        pattern = self.rhs_params[0]
        backend_op = connection.ops.gis_operators[self.lookup_name]
        if hasattr(backend_op, "check_relate_argument"):
            backend_op.check_relate_argument(pattern)
        elif not isinstance(pattern, str) or not self.pattern_regex.match(pattern):
            raise ValueError('Invalid intersection matrix pattern "%s".' % pattern)
        sql, params = super().process_rhs(compiler, connection)
        return sql, params + [pattern]
