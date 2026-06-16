class SitemapIndexItem:
    location: str
    last_mod: bool = None

    # RemovedInDjango50Warning
    def __str__(self):
        msg = (
            "Calling `__str__` on SitemapIndexItem is deprecated, use the `location` "
            "attribute instead."
        )
        warnings.warn(msg, RemovedInDjango50Warning, stacklevel=2)
        return self.location
