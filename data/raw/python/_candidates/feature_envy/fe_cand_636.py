def as_sql(self, compiler, connection):
    # Resolve the condition in Join.filtered_relation.
    query = compiler.query
    where = query.build_filtered_relation_q(self.condition, reuse=set(self.path))
    return compiler.compile(where)
