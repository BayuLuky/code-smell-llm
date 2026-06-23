def __init__(self, app: App, **options: t.Any) -> None:
    if "loader" not in options:
        options["loader"] = app.create_global_jinja_loader()
    BaseEnvironment.__init__(self, **options)
    self.app = app
