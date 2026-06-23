def _fail(self, *args: t.Any, **kwargs: t.Any) -> t.NoReturn:
    raise RuntimeError(
        "The session is unavailable because no secret "
        "key was set.  Set the secret_key on the "
        "application to something unique and secret."
    )
