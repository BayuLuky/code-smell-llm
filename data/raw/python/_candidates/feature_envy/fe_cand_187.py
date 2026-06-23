def _get_default_requests(cls):
    """Collect default request values.

    This method combines the information present in ``__metadata_request__*``
    class attributes, as well as determining request keys from method
    signatures.
    """
    requests = MetadataRequest(owner=cls.__name__)

    for method in SIMPLE_METHODS:
        setattr(
            requests,
            method,
            cls._build_request_for_signature(router=requests, method=method),
        )

    # Then overwrite those defaults with the ones provided in
    # __metadata_request__* attributes. Defaults set in
    # __metadata_request__* attributes take precedence over signature
    # sniffing.

    # need to go through the MRO since this is a class attribute and
    # ``vars`` doesn't report the parent class attributes. We go through
    # the reverse of the MRO so that child classes have precedence over
    # their parents.
    defaults = dict()
    for base_class in reversed(inspect.getmro(cls)):
        base_defaults = {
            attr: value
            for attr, value in vars(base_class).items()
            if "__metadata_request__" in attr
        }
        defaults.update(base_defaults)
    defaults = dict(sorted(defaults.items()))

    for attr, value in defaults.items():
        # we don't check for attr.startswith() since python prefixes attrs
        # starting with __ with the `_ClassName`.
        substr = "__metadata_request__"
        method = attr[attr.index(substr) + len(substr) :]
        for prop, alias in value.items():
            getattr(requests, method).add_request(param=prop, alias=alias)

    return requests
