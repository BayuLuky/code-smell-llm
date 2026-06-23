def make_env(
    self, overrides: t.Optional[t.Mapping[str, t.Optional[str]]] = None
) -> t.Mapping[str, t.Optional[str]]:
    """Returns the environment overrides for invoking a script."""
    rv = dict(self.env)
    if overrides:
        rv.update(overrides)
    return rv
