class DistanceLookupBase(GISLookup):
    distance = True
    sql_template = "%(func)s(%(lhs)s, %(rhs)s) %(op)s %(value)s"

    def process_rhs_params(self):
        if not 1 <= len(self.rhs_params) <= 3:
            raise ValueError(
                "2, 3, or 4-element tuple required for '%s' lookup." % self.lookup_name
            )
        elif len(self.rhs_params) == 3 and self.rhs_params[2] != "spheroid":
            raise ValueError(
                "For 4-element tuples the last argument must be the 'spheroid' "
                "directive."
            )

        # Check if the second parameter is a band index.
        if len(self.rhs_params) > 1 and self.rhs_params[1] != "spheroid":
            self.process_band_indices()

    def process_distance(self, compiler, connection):
        dist_param = self.rhs_params[0]
        return (
            compiler.compile(dist_param.resolve_expression(compiler.query))
            if hasattr(dist_param, "resolve_expression")
            else (
                "%s",
                connection.ops.get_distance(
                    self.lhs.output_field, self.rhs_params, self.lookup_name
                ),
            )
        )
