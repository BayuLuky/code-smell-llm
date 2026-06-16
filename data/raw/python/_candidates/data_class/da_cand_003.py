class OLMap(self.widget):
    template_name = self.map_template
    geom_type = db_field.geom_type

    wms_options = ""
    if self.wms_options:
        wms_options = ["%s: '%s'" % pair for pair in self.wms_options.items()]
        wms_options = ", %s" % ", ".join(wms_options)

    params = {
        "default_lon": self.default_lon,
        "default_lat": self.default_lat,
        "default_zoom": self.default_zoom,
        "display_wkt": self.debug or self.display_wkt,
        "geom_type": OGRGeomType(db_field.geom_type),
        "field_name": db_field.name,
        "is_collection": is_collection,
        "scrollable": self.scrollable,
        "layerswitcher": self.layerswitcher,
        "collection_type": collection_type,
        "is_generic": db_field.geom_type == "GEOMETRY",
        "is_linestring": db_field.geom_type
        in ("LINESTRING", "MULTILINESTRING"),
        "is_polygon": db_field.geom_type in ("POLYGON", "MULTIPOLYGON"),
        "is_point": db_field.geom_type in ("POINT", "MULTIPOINT"),
        "num_zoom": self.num_zoom,
        "max_zoom": self.max_zoom,
        "min_zoom": self.min_zoom,
        "units": self.units,  # likely should get from object
        "max_resolution": self.max_resolution,
        "max_extent": self.max_extent,
        "modifiable": self.modifiable,
        "mouse_position": self.mouse_position,
        "scale_text": self.scale_text,
        "map_width": self.map_width,
        "map_height": self.map_height,
        "point_zoom": self.point_zoom,
        "srid": self.map_srid,
        "display_srid": self.display_srid,
        "wms_url": self.wms_url,
        "wms_layer": self.wms_layer,
        "wms_name": self.wms_name,
        "wms_options": wms_options,
        "debug": self.debug,
    }
