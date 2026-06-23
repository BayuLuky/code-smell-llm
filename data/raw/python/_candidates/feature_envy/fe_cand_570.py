def replace(self, *args, **kwargs) -> Request:
    body_passed = kwargs.get("body", None) is not None
    data = kwargs.pop("data", None)
    data_passed = data is not None

    if body_passed and data_passed:
        warnings.warn("Both body and data passed. data will be ignored")
    elif not body_passed and data_passed:
        kwargs["body"] = self._dumps(data)

    return super().replace(*args, **kwargs)
