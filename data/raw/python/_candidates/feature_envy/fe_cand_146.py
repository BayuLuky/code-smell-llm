def from_settings(
    cls, settings: Settings, crawler: Optional[Crawler] = None
) -> Self:
    mwlist = cls._get_mwlist_from_settings(settings)
    middlewares = []
    enabled = []
    for clspath in mwlist:
        try:
            mwcls = load_object(clspath)
            mw = create_instance(mwcls, settings, crawler)
            middlewares.append(mw)
            enabled.append(clspath)
        except NotConfigured as e:
            if e.args:
                logger.warning(
                    "Disabled %(clspath)s: %(eargs)s",
                    {"clspath": clspath, "eargs": e.args[0]},
                    extra={"crawler": crawler},
                )

    logger.info(
        "Enabled %(componentname)ss:\n%(enabledlist)s",
        {
            "componentname": cls.component_name,
            "enabledlist": pprint.pformat(enabled),
        },
        extra={"crawler": crawler},
    )
    return cls(*middlewares)
