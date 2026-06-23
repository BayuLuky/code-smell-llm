class Area(MeasureBase):
    STANDARD_UNIT = AREA_PREFIX + Distance.STANDARD_UNIT
    # Getting the square units values and the alias dictionary.
    UNITS = {"%s%s" % (AREA_PREFIX, k): v**2 for k, v in Distance.UNITS.items()}
    ALIAS = {k: "%s%s" % (AREA_PREFIX, v) for k, v in Distance.ALIAS.items()}
    LALIAS = {k.lower(): v for k, v in ALIAS.items()}

    def __truediv__(self, other):
        if isinstance(other, NUMERIC_TYPES):
            return self.__class__(
                default_unit=self._default_unit,
                **{self.STANDARD_UNIT: (self.standard / other)},
            )
        else:
            raise TypeError(
                "%(class)s must be divided by a number" % {"class": pretty_name(self)}
            )
