def filter(self, record: logging.LogRecord) -> bool:
    if any(record.name.startswith(logger + ".") for logger in self.loggers):
        record.name = record.name.split(".", 1)[0]
    return True
