def ensure_registered(cls):
    """
    Attempt to register all the data source drivers.
    """
    # Only register all if the driver counts are 0 (or else all drivers
    # will be registered over and over again)
    if not vcapi.get_driver_count():
        vcapi.register_all()
    if not rcapi.get_driver_count():
        rcapi.register_all()
