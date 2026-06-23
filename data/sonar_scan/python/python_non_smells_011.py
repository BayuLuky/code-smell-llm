class DataSource(GDALBase):
    "Wraps an OGR Data Source object."
    destructor = capi.destroy_ds

    def __init__(self, ds_input, ds_driver=False, write=False, encoding="utf-8"):
        # The write flag.
        if write:
            self._write = 1
        else:
            self._write = 0
        # See also https://gdal.org/development/rfc/rfc23_ogr_unicode.html
        self.encoding = encoding

        Driver.ensure_registered()

        if isinstance(ds_input, (str, Path)):
            # The data source driver is a void pointer.
            ds_driver = Driver.ptr_type()
            try:
                # OGROpen will auto-detect the data source type.
                ds = capi.open_ds(force_bytes(ds_input), self._write, byref(ds_driver))
            except GDALException:
                # Making the error message more clear rather than something
                # like "Invalid pointer returned from OGROpen".
                raise GDALException('Could not open the datasource at "%s"' % ds_input)
        elif isinstance(ds_input, self.ptr_type) and isinstance(
            ds_driver, Driver.ptr_type
        ):
            ds = ds_input
        else:
            raise GDALException("Invalid data source input type: %s" % type(ds_input))

        if ds:
            self.ptr = ds
            self.driver = Driver(ds_driver)
        else:
            # Raise an exception if the returned pointer is NULL
            raise GDALException('Invalid data source file "%s"' % ds_input)

    def __getitem__(self, index):
        "Allows use of the index [] operator to get a layer at the index."
        if isinstance(index, str):
            try:
                layer = capi.get_layer_by_name(self.ptr, force_bytes(index))
            except GDALException:
                raise IndexError("Invalid OGR layer name given: %s." % index)
        elif isinstance(index, int):
            if 0 <= index < self.layer_count:
                layer = capi.get_layer(self._ptr, index)
            else:
                raise IndexError(
                    "Index out of range when accessing layers in a datasource: %s."
                    % index
                )
        else:
            raise TypeError("Invalid index type: %s" % type(index))
        return Layer(layer, self)

    def __len__(self):
        "Return the number of layers within the data source."
        return self.layer_count

    def __str__(self):
        "Return OGR GetName and Driver for the Data Source."
        return "%s (%s)" % (self.name, self.driver)

    @property
    def layer_count(self):
        "Return the number of layers in the data source."
        return capi.get_layer_count(self._ptr)

    @property
    def name(self):
        "Return the name of the data source."
        name = capi.get_ds_name(self._ptr)
        return force_str(name, self.encoding, strings_only=True)
