def __repr__(self) -> str:
    ctx = _cv_app.get(None)
    if ctx is not None:
        return f"<flask.g of '{ctx.app.name}'>"
    return object.__repr__(self)
