def _load_plugin_commands(self) -> None:
    if self._loaded_plugin_commands:
        return

    if sys.version_info >= (3, 10):
        from importlib import metadata
    else:
        # Use a backport on Python < 3.10. We technically have
        # importlib.metadata on 3.8+, but the API changed in 3.10,
        # so use the backport for consistency.
        import importlib_metadata as metadata

    for ep in metadata.entry_points(group="flask.commands"):
        self.add_command(ep.load(), ep.name)

    self._loaded_plugin_commands = True
