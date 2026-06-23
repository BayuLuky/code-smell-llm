class OracleGeometryColumns(models.Model):
    "Maps to the Oracle USER_SDO_GEOM_METADATA table."
    table_name = models.CharField(max_length=32)
    column_name = models.CharField(max_length=1024)
    srid = models.IntegerField(primary_key=True)
    # TODO: Add support for `diminfo` column (type MDSYS.SDO_DIM_ARRAY).

    class Meta:
        app_label = "gis"
        db_table = "USER_SDO_GEOM_METADATA"
        managed = False

    def __str__(self):
        return "%s - %s (SRID: %s)" % (self.table_name, self.column_name, self.srid)

    @classmethod
    def table_name_col(cls):
        """
        Return the name of the metadata column used to store the feature table
        name.
        """
        return "table_name"

    @classmethod
    def geom_col_name(cls):
        """
        Return the name of the metadata column used to store the feature
        geometry column.
        """
        return "column_name"
