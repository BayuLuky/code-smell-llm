def match(self, path):
    match = self.regex.search(path)
    if match:
        # RoutePattern doesn't allow non-named groups so args are ignored.
        kwargs = match.groupdict()
        for key, value in kwargs.items():
            converter = self.converters[key]
            try:
                kwargs[key] = converter.to_python(value)
            except ValueError:
                return None
        return path[match.end() :], (), kwargs
    return None
