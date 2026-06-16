class DatabaseWrapper(PsycopgDatabaseWrapper):
    SchemaEditorClass = PostGISSchemaEditor

    _type_infos = {
        "geometry": {},
        "geography": {},
        "raster": {},
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("alias", "") != NO_DB_ALIAS:
            self.features = DatabaseFeatures(self)
            self.ops = PostGISOperations(self)
            self.introspection = PostGISIntrospection(self)

    def prepare_database(self):
        super().prepare_database()
        # Check that postgis extension is installed.
        with self.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_extension WHERE extname = %s", ["postgis"])
            if bool(cursor.fetchone()):
                return
            cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")
            if is_psycopg3:
                # Ensure adapters are registers if PostGIS is used within this
                # connection.
                self.register_geometry_adapters(self.connection, True)

    def get_new_connection(self, conn_params):
        connection = super().get_new_connection(conn_params)
        if is_psycopg3:
            self.register_geometry_adapters(connection)
        return connection

    if is_psycopg3:

        def _register_type(self, pg_connection, typename):
            registry = self._type_infos[typename]
            try:
                info = registry[self.alias]
            except KeyError:
                info = TypeInfo.fetch(pg_connection, typename)
                registry[self.alias] = info

            if info:  # Can be None if the type does not exist (yet).
                info.register(pg_connection)
                pg_connection.adapters.register_loader(info.oid, TextLoader)
                pg_connection.adapters.register_loader(info.oid, TextBinaryLoader)

            return info.oid if info else None

        def register_geometry_adapters(self, pg_connection, clear_caches=False):
            if clear_caches:
                for typename in self._type_infos:
                    self._type_infos[typename].pop(self.alias, None)

            geo_oid = self._register_type(pg_connection, "geometry")
            geog_oid = self._register_type(pg_connection, "geography")
            raster_oid = self._register_type(pg_connection, "raster")

            PostGISTextDumper, PostGISBinaryDumper = postgis_adapters(
                geo_oid, geog_oid, raster_oid
            )
            pg_connection.adapters.register_dumper(PostGISAdapter, PostGISTextDumper)
            pg_connection.adapters.register_dumper(PostGISAdapter, PostGISBinaryDumper)
