def __getitem__(self, index):
    "Return the Point at the given index."
    if 0 <= index < self.point_count:
        x, y, z = c_double(), c_double(), c_double()
        capi.get_point(self.ptr, index, byref(x), byref(y), byref(z))
        dim = self.coord_dim
        if dim == 1:
            return (x.value,)
        elif dim == 2:
            return (x.value, y.value)
        elif dim == 3:
            return (x.value, y.value, z.value)
    else:
        raise IndexError(
            "Index out of range when accessing points of a line string: %s." % index
        )
