class RenderableErrorMixin(RenderableMixin):
    def as_json(self, escape_html=False):
        return json.dumps(self.get_json_data(escape_html))

    def as_text(self):
        return self.render(self.template_name_text)

    def as_ul(self):
        return self.render(self.template_name_ul)
