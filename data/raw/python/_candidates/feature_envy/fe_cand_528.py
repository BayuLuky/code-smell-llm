def update(self, trans):
    # Merge if plural function is the same, else prepend.
    for cat, plural in zip(self._catalogs, self._plurals):
        if trans.plural.__code__ == plural.__code__:
            cat.update(trans._catalog)
            break
    else:
        self._catalogs.insert(0, trans._catalog.copy())
        self._plurals.insert(0, trans.plural)
