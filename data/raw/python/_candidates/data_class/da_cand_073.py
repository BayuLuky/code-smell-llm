class Fieldset:
    def __init__(
        self,
        form,
        name=None,
        readonly_fields=(),
        fields=(),
        classes=(),
        description=None,
        model_admin=None,
    ):
        self.form = form
        self.name, self.fields = name, fields
        self.classes = " ".join(classes)
        self.description = description
        self.model_admin = model_admin
        self.readonly_fields = readonly_fields

    @property
    def media(self):
        if "collapse" in self.classes:
            return forms.Media(js=["admin/js/collapse.js"])
        return forms.Media()

    def __iter__(self):
        for field in self.fields:
            yield Fieldline(
                self.form, field, self.readonly_fields, model_admin=self.model_admin
            )
