class RegexField(CharField):
    def __init__(self, regex, **kwargs):
        """
        regex can be either a string or a compiled regular expression object.
        """
        kwargs.setdefault("strip", False)
        super().__init__(**kwargs)
        self._set_regex(regex)

    def _get_regex(self):
        return self._regex

    def _set_regex(self, regex):
        if isinstance(regex, str):
            regex = re.compile(regex)
        self._regex = regex
        if (
            hasattr(self, "_regex_validator")
            and self._regex_validator in self.validators
        ):
            self.validators.remove(self._regex_validator)
        self._regex_validator = validators.RegexValidator(regex=regex)
        self.validators.append(self._regex_validator)

    regex = property(_get_regex, _set_regex)
