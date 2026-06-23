def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
    if not args and self.no_args_is_help:
        # Attempt to load --env-file and --app early in case they
        # were given as env vars. Otherwise no_args_is_help will not
        # see commands from app.cli.
        _env_file_option.handle_parse_result(ctx, {}, [])
        _app_option.handle_parse_result(ctx, {}, [])

    return super().parse_args(ctx, args)
