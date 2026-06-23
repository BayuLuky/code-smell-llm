def to_info_dict(self) -> t.Dict[str, t.Any]:
    info_dict = super().to_info_dict()
    info_dict.update(mode=self.mode, encoding=self.encoding)
    return info_dict
