class PatternLookup(BuiltinLookup):
    param_pattern = "%%%s%%"
    prepare_rhs = False

    def get_rhs_op(self, connection, rhs):
        # Assume we are in startswith. We need to produce SQL like:
        #     col LIKE %s, ['thevalue%']
        # For python values we can (and should) do that directly in Python,
        # but if the value is for example reference to other column, then
        # we need to add the % pattern match to the lookup by something like
        #     col LIKE othercol || '%%'
        # So, for Python values we don't need any special pattern, but for
        # SQL reference values or SQL transformations we need the correct
        # pattern added.
        if hasattr(self.rhs, "as_sql") or self.bilateral_transforms:
            pattern = connection.pattern_ops[self.lookup_name].format(
                connection.pattern_esc
            )
            return pattern.format(rhs)
        else:
            return super().get_rhs_op(connection, rhs)

    def process_rhs(self, qn, connection):
        rhs, params = super().process_rhs(qn, connection)
        if self.rhs_is_direct_value() and params and not self.bilateral_transforms:
            params[0] = self.param_pattern % connection.ops.prep_for_like_query(
                params[0]
            )
        return rhs, params
