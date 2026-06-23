def __init__(cls, name: str, bases: Tuple[type, ...], clsdict_: Dict[str, Any]):
    meta = cls.__class__
    old = meta.deprecated_class
    if old in bases and not (warn_once and meta.warned_on_subclass):
        meta.warned_on_subclass = True
        msg = subclass_warn_message.format(
            cls=_clspath(cls),
            old=_clspath(old, old_class_path),
            new=_clspath(new_class, new_class_path),
        )
        if warn_once:
            msg += " (warning only on first subclass, there may be others)"
        warnings.warn(msg, warn_category, stacklevel=2)
    super().__init__(name, bases, clsdict_)
