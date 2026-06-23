class datetime(real_datetime):
    def strftime(self, fmt):
        return strftime(self, fmt)

    @classmethod
    def combine(cls, date, time):
        return cls(
            date.year,
            date.month,
            date.day,
            time.hour,
            time.minute,
            time.second,
            time.microsecond,
            time.tzinfo,
        )

    def date(self):
        return date(self.year, self.month, self.day)
