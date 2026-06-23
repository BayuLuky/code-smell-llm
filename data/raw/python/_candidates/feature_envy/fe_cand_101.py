def get_command(self, ctx, cmd_name):
    # Step one: bulitin commands as normal
    rv = click.Group.get_command(self, ctx, cmd_name)
    if rv is not None:
        return rv

    # Step two: find the config object and ensure it's there.  This
    # will create the config object is missing.
    cfg = ctx.ensure_object(Config)

    # Step three: look up an explicit command alias in the config
    if cmd_name in cfg.aliases:
        actual_cmd = cfg.aliases[cmd_name]
        return click.Group.get_command(self, ctx, actual_cmd)

    # Alternative option: if we did not find an explicit alias we
    # allow automatic abbreviation of the command.  "status" for
    # instance will match "st".  We only allow that however if
    # there is only one command.
    matches = [
        x for x in self.list_commands(ctx) if x.lower().startswith(cmd_name.lower())
    ]
    if not matches:
        return None
    elif len(matches) == 1:
        return click.Group.get_command(self, ctx, matches[0])
    ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")
