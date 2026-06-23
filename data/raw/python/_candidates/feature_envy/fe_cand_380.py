def database_backwards(self, app_label, schema_editor, from_state, to_state):
    if not router.allow_migrate(schema_editor.connection.alias, app_label):
        return
    if self.extension_exists(schema_editor, self.name):
        schema_editor.execute(
            "DROP EXTENSION IF EXISTS %s" % schema_editor.quote_name(self.name)
        )
    # Clear cached, stale oids.
    get_hstore_oids.cache_clear()
    get_citext_oids.cache_clear()
