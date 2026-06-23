def is_email_simple(value):
    """Return True if value looks like an email address."""
    # An @ must be in the middle of the value.
    if "@" not in value or value.startswith("@") or value.endswith("@"):
        return False
    try:
        p1, p2 = value.split("@")
    except ValueError:
        # value contains more than one @.
        return False
    # Dot must be in p2 (e.g. example.com)
    if "." not in p2 or p2.startswith("."):
        return False
    return True
