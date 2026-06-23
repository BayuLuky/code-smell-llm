def _serialize(self):
    """Serialize the object.

    Returns
    -------
    obj : list
        A serialized version of the instance in the form of a list.
    """
    result = list()
    for route in self._routes:
        result.append({"callee": route.callee, "caller": route.caller})
    return result
