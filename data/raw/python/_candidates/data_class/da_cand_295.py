class GenericIPAddressField(CharField):
    def __init__(self, *, protocol="both", unpack_ipv4=False, **kwargs):
        self.unpack_ipv4 = unpack_ipv4
        self.default_validators = validators.ip_address_validators(
            protocol, unpack_ipv4
        )[0]
        super().__init__(**kwargs)

    def to_python(self, value):
        if value in self.empty_values:
            return ""
        value = value.strip()
        if value and ":" in value:
            return clean_ipv6_address(value, self.unpack_ipv4)
        return value
