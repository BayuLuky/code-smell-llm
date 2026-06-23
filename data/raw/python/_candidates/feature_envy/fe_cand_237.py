def __init_subclass__(cls, **kwargs: t.Any) -> None:
    super().__init_subclass__(**kwargs)

    if "methods" not in cls.__dict__:
        methods = set()

        for base in cls.__bases__:
            if getattr(base, "methods", None):
                methods.update(base.methods)  # type: ignore[attr-defined]

        for key in http_method_funcs:
            if hasattr(cls, key):
                methods.add(key.upper())

        if methods:
            cls.methods = methods
