def _configure(self, options, dont_fail=False):
    """Configure the exporter by popping options from the ``options`` dict.
    If dont_fail is set, it won't raise an exception on unexpected options
    (useful for using with keyword arguments in subclasses ``__init__`` methods)
    """
    self.encoding = options.pop("encoding", None)
    self.fields_to_export = options.pop("fields_to_export", None)
    self.export_empty_fields = options.pop("export_empty_fields", False)
    self.indent = options.pop("indent", None)
    if not dont_fail and options:
        raise TypeError(f"Unexpected options: {', '.join(options.keys())}")
