class build_ext_subclass(build_ext):
    def finalize_options(self):
        build_ext.finalize_options(self)
        if self.parallel is None:
            # Do not override self.parallel if already defined by
            # command-line flag (--parallel or -j)

            parallel = os.environ.get("SKLEARN_BUILD_PARALLEL")
            if parallel:
                self.parallel = int(parallel)
        if self.parallel:
            print("setting parallel=%d " % self.parallel)

    def build_extensions(self):
        from sklearn._build_utils.openmp_helpers import get_openmp_flag

        # Always use NumPy 1.7 C API for all compiled extensions.
        # See: https://numpy.org/doc/stable/reference/c-api/deprecations.html
        DEFINE_MACRO_NUMPY_C_API = (
            "NPY_NO_DEPRECATED_API",
            "NPY_1_7_API_VERSION",
        )
        for ext in self.extensions:
            ext.define_macros.append(DEFINE_MACRO_NUMPY_C_API)

        if sklearn._OPENMP_SUPPORTED:
            openmp_flag = get_openmp_flag()

            for e in self.extensions:
                e.extra_compile_args += openmp_flag
                e.extra_link_args += openmp_flag

        build_ext.build_extensions(self)

    def run(self):
        # Specifying `build_clib` allows running `python setup.py develop`
        # fully from a fresh clone.
        self.run_command("build_clib")
        build_ext.run(self)
