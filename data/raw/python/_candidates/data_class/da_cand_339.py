class TimingMixin:
    def _initialize_times(self):
        self.created_time = now()
        self.accessed_time = self.created_time
        self.modified_time = self.created_time

    def _update_accessed_time(self):
        self.accessed_time = now()

    def _update_modified_time(self):
        self.modified_time = now()
