def __call__(cls, *args: Any, **kwargs: Any) -> Any:
    old = DeprecatedClass.deprecated_class
    if cls is old:
        msg = instance_warn_message.format(
            cls=_clspath(cls, old_class_path),
            new=_clspath(new_class, new_class_path),
        )
        warnings.warn(msg, warn_category, stacklevel=2)
    return super().__call__(*args, **kwargs)
