def get_metadata_routing(self):
    """Get metadata routing of this object.

    Please check :ref:`User Guide <metadata_routing>` on how the routing
    mechanism works.

    .. versionadded:: 1.4

    Returns
    -------
    routing : MetadataRouter
        A :class:`~sklearn.utils.metadata_routing.MetadataRouter` encapsulating
        routing information.
    """

    router = (
        MetadataRouter(owner=self.__class__.__name__)
        .add_self_request(self)
        .add(
            estimator=self.estimator,
            method_mapping=MethodMapping()
            .add(callee="fit", caller="fit")
            .add(callee="partial_fit", caller="partial_fit"),
        )
    )
    return router
