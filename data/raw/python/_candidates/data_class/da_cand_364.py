class TempMemmap:
    """
    Parameters
    ----------
    data
    mmap_mode : str, default='r'
    """

    def __init__(self, data, mmap_mode="r"):
        self.mmap_mode = mmap_mode
        self.data = data

    def __enter__(self):
        data_read_only, self.temp_folder = create_memmap_backed_data(
            self.data, mmap_mode=self.mmap_mode, return_folder=True
        )
        return data_read_only

    def __exit__(self, exc_type, exc_val, exc_tb):
        _delete_folder(self.temp_folder)
