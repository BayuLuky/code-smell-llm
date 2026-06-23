def formfield_for_dbfield(self, db_field, request, **kwargs):
    """
    Overloaded from ModelAdmin so that an OpenLayersWidget is used
    for viewing/editing 2D GeometryFields (OpenLayers 2 does not support
    3D editing).
    """
    if isinstance(db_field, models.GeometryField) and db_field.dim < 3:
        # Setting the widget with the newly defined widget.
        kwargs["widget"] = self.get_map_widget(db_field)
        return db_field.formfield(**kwargs)
    else:
        return super().formfield_for_dbfield(db_field, request, **kwargs)
