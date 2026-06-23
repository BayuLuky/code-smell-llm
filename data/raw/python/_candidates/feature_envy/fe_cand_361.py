def list_commands(self, ctx: Context) -> t.List[str]:
    rv: t.Set[str] = set()

    for source in self.sources:
        rv.update(source.list_commands(ctx))

    return sorted(rv)
