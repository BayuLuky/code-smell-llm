class Lookup(Expression):
    lookup_name = None
    prepare_rhs = True
    can_use_none_as_rhs = False

    def __init__(self, lhs, rhs):
        self.lhs, self.rhs = lhs, rhs
        self.rhs = self.get_prep_lookup()
        self.lhs = self.get_prep_lhs()
        if hasattr(self.lhs, "get_bilateral_transforms"):
            bilateral_transforms = self.lhs.get_bilateral_transforms()
        else:
            bilateral_transforms = []
        if bilateral_transforms:
            # Warn the user as soon as possible if they are trying to apply
            # a bilateral transformation on a nested QuerySet: that won't work.
            from django.db.models.sql.query import Query  # avoid circular import

            if isinstance(rhs, Query):
                raise NotImplementedError(
                    "Bilateral transformations on nested querysets are not implemented."
                )
        self.bilateral_transforms = bilateral_transforms

    def apply_bilateral_transforms(self, value):
        for transform in self.bilateral_transforms:
            value = transform(value)
        return value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.lhs!r}, {self.rhs!r})"

    def batch_process_rhs(self, compiler, connection, rhs=None):
        if rhs is None:
            rhs = self.rhs
        if self.bilateral_transforms:
            sqls, sqls_params = [], []
            for p in rhs:
                value = Value(p, output_field=self.lhs.output_field)
                value = self.apply_bilateral_transforms(value)
                value = value.resolve_expression(compiler.query)
                sql, sql_params = compiler.compile(value)
                sqls.append(sql)
                sqls_params.extend(sql_params)
        else:
            _, params = self.get_db_prep_lookup(rhs, connection)
            sqls, sqls_params = ["%s"] * len(params), params
        return sqls, sqls_params

    def get_source_expressions(self):
        if self.rhs_is_direct_value():
            return [self.lhs]
        return [self.lhs, self.rhs]

    def set_source_expressions(self, new_exprs):
        if len(new_exprs) == 1:
            self.lhs = new_exprs[0]
        else:
            self.lhs, self.rhs = new_exprs

    def get_prep_lookup(self):
        if not self.prepare_rhs or hasattr(self.rhs, "resolve_expression"):
            return self.rhs
        if hasattr(self.lhs, "output_field"):
            if hasattr(self.lhs.output_field, "get_prep_value"):
                return self.lhs.output_field.get_prep_value(self.rhs)
        elif self.rhs_is_direct_value():
            return Value(self.rhs)
        return self.rhs

    def get_prep_lhs(self):
        if hasattr(self.lhs, "resolve_expression"):
            return self.lhs
        return Value(self.lhs)

    def get_db_prep_lookup(self, value, connection):
        return ("%s", [value])

    def process_lhs(self, compiler, connection, lhs=None):
        lhs = lhs or self.lhs
        if hasattr(lhs, "resolve_expression"):
            lhs = lhs.resolve_expression(compiler.query)
        sql, params = compiler.compile(lhs)
        if isinstance(lhs, Lookup):
            # Wrapped in parentheses to respect operator precedence.
            sql = f"({sql})"
        return sql, params

    def process_rhs(self, compiler, connection):
        value = self.rhs
        if self.bilateral_transforms:
            if self.rhs_is_direct_value():
                # Do not call get_db_prep_lookup here as the value will be
                # transformed before being used for lookup
                value = Value(value, output_field=self.lhs.output_field)
            value = self.apply_bilateral_transforms(value)
            value = value.resolve_expression(compiler.query)
        if hasattr(value, "as_sql"):
            sql, params = compiler.compile(value)
            # Ensure expression is wrapped in parentheses to respect operator
            # precedence but avoid double wrapping as it can be misinterpreted
            # on some backends (e.g. subqueries on SQLite).
            if sql and sql[0] != "(":
                sql = "(%s)" % sql
            return sql, params
        else:
            return self.get_db_prep_lookup(value, connection)

    def rhs_is_direct_value(self):
        return not hasattr(self.rhs, "as_sql")

    def get_group_by_cols(self):
        cols = []
        for source in self.get_source_expressions():
            cols.extend(source.get_group_by_cols())
        return cols

    def as_oracle(self, compiler, connection):
        # Oracle doesn't allow EXISTS() and filters to be compared to another
        # expression unless they're wrapped in a CASE WHEN.
        wrapped = False
        exprs = []
        for expr in (self.lhs, self.rhs):
            if connection.ops.conditional_expression_supported_in_where_clause(expr):
                expr = Case(When(expr, then=True), default=False)
                wrapped = True
            exprs.append(expr)
        lookup = type(self)(*exprs) if wrapped else self
        return lookup.as_sql(compiler, connection)

    @cached_property
    def output_field(self):
        return BooleanField()

    @property
    def identity(self):
        return self.__class__, self.lhs, self.rhs

    def __eq__(self, other):
        if not isinstance(other, Lookup):
            return NotImplemented
        return self.identity == other.identity

    def __hash__(self):
        return hash(make_hashable(self.identity))

    def resolve_expression(
        self, query=None, allow_joins=True, reuse=None, summarize=False, for_save=False
    ):
        c = self.copy()
        c.is_summary = summarize
        c.lhs = self.lhs.resolve_expression(
            query, allow_joins, reuse, summarize, for_save
        )
        if hasattr(self.rhs, "resolve_expression"):
            c.rhs = self.rhs.resolve_expression(
                query, allow_joins, reuse, summarize, for_save
            )
        return c

    def select_format(self, compiler, sql, params):
        # Wrap filters with a CASE WHEN expression if a database backend
        # (e.g. Oracle) doesn't support boolean expression in SELECT or GROUP
        # BY list.
        if not compiler.connection.features.supports_boolean_expr_in_select_clause:
            sql = f"CASE WHEN {sql} THEN 1 ELSE 0 END"
        return sql, params
