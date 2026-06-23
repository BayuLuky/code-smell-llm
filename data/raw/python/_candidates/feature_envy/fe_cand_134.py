def list_commands(self, ctx: click.Context) -> list[str]:
    self._load_plugin_commands()
    # Start with the built-in and plugin commands.
    rv = set(super().list_commands(ctx))
    info = ctx.ensure_object(ScriptInfo)

    # Add commands provided by the app, showing an error and
    # continuing if the app couldn't be loaded.
    try:
        rv.update(info.load_app().cli.list_commands(ctx))
    except NoAppException as e:
        # When an app couldn't be loaded, show the error message
        # without the traceback.
        click.secho(f"Error: {e.format_message()}\n", err=True, fg="red")
    except Exception:
        # When any other errors occurred during loading, show the
        # full traceback.
        click.secho(f"{traceback.format_exc()}\n", err=True, fg="red")

    return sorted(rv)
