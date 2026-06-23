class IOBase(GEOSBase):
    "Base class for GEOS I/O objects."

    def __init__(self):
        # Getting the pointer with the constructor.
        self.ptr = self._constructor()
        # Loading the real destructor function at this point as doing it in
        # __del__ is too late (import error).
        self.destructor.func
