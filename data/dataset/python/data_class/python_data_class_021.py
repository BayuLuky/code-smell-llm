class WarningInfo:
    action: "warnings._ActionKind"
    message: str = ""
    category: type[Warning] = Warning

    def to_filterwarning_str(self):
        if self.category.__module__ == "builtins":
            category = self.category.__name__
        else:
            category = f"{self.category.__module__}.{self.category.__name__}"

        return f"{self.action}:{self.message}:{category}"
