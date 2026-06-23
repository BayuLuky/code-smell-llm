def to_info_dict(self) -> t.Dict[str, t.Any]:
    info_dict = super().to_info_dict()
    info_dict["types"] = [t.to_info_dict() for t in self.types]
    return info_dict
