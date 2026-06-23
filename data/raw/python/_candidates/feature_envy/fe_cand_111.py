def convert(
    self, value: t.Any, param: click.Parameter | None, ctx: click.Context | None
) -> t.Any:
    try:
        import ssl
    except ImportError:
        raise click.BadParameter(
            'Using "--cert" requires Python to be compiled with SSL support.',
            ctx,
            param,
        ) from None

    try:
        return self.path_type(value, param, ctx)
    except click.BadParameter:
        value = click.STRING(value, param, ctx).lower()

        if value == "adhoc":
            try:
                import cryptography  # noqa: F401
            except ImportError:
                raise click.BadParameter(
                    "Using ad-hoc certificates requires the cryptography library.",
                    ctx,
                    param,
                ) from None

            return value

        obj = import_string(value, silent=True)

        if isinstance(obj, ssl.SSLContext):
            return obj

        raise
