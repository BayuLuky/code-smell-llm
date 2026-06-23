def _warn_overlap(self, message, kwargs):
    """Warn if there is any overlap between ``self._kwargs`` and ``kwargs``.

    This method is intended to be used to check for overlap between
    ``self._kwargs`` and ``kwargs`` passed as metadata.
    """
    _kwargs = set() if self._kwargs is None else set(self._kwargs.keys())
    overlap = _kwargs.intersection(kwargs.keys())
    if overlap:
        warnings.warn(
            f"{message} Overlapping parameters are: {overlap}", UserWarning
        )
