class InMemoryFileNode(ContentFile, TimingMixin):
    """
    Helper class representing an in-memory file node.

    Handle unicode/bytes conversion during I/O operations and record creation,
    modification, and access times.
    """

    def __init__(self, content="", name=""):
        self.file = None
        self._content_type = type(content)
        self._initialize_stream()
        self._initialize_times()

    def open(self, mode):
        self._convert_stream_content(mode)
        self._update_accessed_time()
        return super().open(mode)

    def write(self, data):
        super().write(data)
        self._update_modified_time()

    def _initialize_stream(self):
        """Initialize underlying stream according to the content type."""
        self.file = io.BytesIO() if self._content_type == bytes else io.StringIO()

    def _convert_stream_content(self, mode):
        """Convert actual file content according to the opening mode."""
        new_content_type = bytes if "b" in mode else str
        # No conversion needed.
        if self._content_type == new_content_type:
            return

        content = self.file.getvalue()
        content = content.encode() if isinstance(content, str) else content.decode()
        self._content_type = new_content_type
        self._initialize_stream()

        self.file.write(content)
