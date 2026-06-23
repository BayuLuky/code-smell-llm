class Distance(MeasureBase):
    STANDARD_UNIT = "m"
    UNITS = {
        "chain": 20.1168,
        "chain_benoit": 20.116782,
        "chain_sears": 20.1167645,
        "british_chain_benoit": 20.1167824944,
        "british_chain_sears": 20.1167651216,
        "british_chain_sears_truncated": 20.116756,
        "cm": 0.01,
        "british_ft": 0.304799471539,
        "british_yd": 0.914398414616,
        "clarke_ft": 0.3047972654,
        "clarke_link": 0.201166195164,
        "fathom": 1.8288,
        "ft": 0.3048,
        "furlong": 201.168,
        "german_m": 1.0000135965,
        "gold_coast_ft": 0.304799710181508,
        "indian_yd": 0.914398530744,
        "inch": 0.0254,
        "km": 1000.0,
        "link": 0.201168,
        "link_benoit": 0.20116782,
        "link_sears": 0.20116765,
        "m": 1.0,
        "mi": 1609.344,
        "mm": 0.001,
        "nm": 1852.0,
        "nm_uk": 1853.184,
        "rod": 5.0292,
        "sears_yd": 0.91439841,
        "survey_ft": 0.304800609601,
        "um": 0.000001,
        "yd": 0.9144,
    }

    # Unit aliases for `UNIT` terms encountered in Spatial Reference WKT.
    ALIAS = {
        "centimeter": "cm",
        "foot": "ft",
        "inches": "inch",
        "kilometer": "km",
        "kilometre": "km",
        "meter": "m",
        "metre": "m",
        "micrometer": "um",
        "micrometre": "um",
        "millimeter": "mm",
        "millimetre": "mm",
        "mile": "mi",
        "yard": "yd",
        "British chain (Benoit 1895 B)": "british_chain_benoit",
        "British chain (Sears 1922)": "british_chain_sears",
        "British chain (Sears 1922 truncated)": "british_chain_sears_truncated",
        "British foot (Sears 1922)": "british_ft",
        "British foot": "british_ft",
        "British yard (Sears 1922)": "british_yd",
        "British yard": "british_yd",
        "Clarke's Foot": "clarke_ft",
        "Clarke's link": "clarke_link",
        "Chain (Benoit)": "chain_benoit",
        "Chain (Sears)": "chain_sears",
        "Foot (International)": "ft",
        "Furrow Long": "furlong",
        "German legal metre": "german_m",
        "Gold Coast foot": "gold_coast_ft",
        "Indian yard": "indian_yd",
        "Link (Benoit)": "link_benoit",
        "Link (Sears)": "link_sears",
        "Nautical Mile": "nm",
        "Nautical Mile (UK)": "nm_uk",
        "US survey foot": "survey_ft",
        "U.S. Foot": "survey_ft",
        "Yard (Indian)": "indian_yd",
        "Yard (Sears)": "sears_yd",
    }
    LALIAS = {k.lower(): v for k, v in ALIAS.items()}

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            return Area(
                default_unit=AREA_PREFIX + self._default_unit,
                **{AREA_PREFIX + self.STANDARD_UNIT: (self.standard * other.standard)},
            )
        elif isinstance(other, NUMERIC_TYPES):
            return self.__class__(
                default_unit=self._default_unit,
                **{self.STANDARD_UNIT: (self.standard * other)},
            )
        else:
            raise TypeError(
                "%(distance)s must be multiplied with number or %(distance)s"
                % {
                    "distance": pretty_name(self.__class__),
                }
            )
