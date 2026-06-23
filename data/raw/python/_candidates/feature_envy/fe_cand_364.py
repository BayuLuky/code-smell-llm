def _try_to_convert_date(self, value: t.Any, format: str) -> t.Optional[datetime]:
    try:
        return datetime.strptime(value, format)
    except ValueError:
        return None
