class RenderableMixin:
    def get_context(self):
        raise NotImplementedError(
            "Subclasses of RenderableMixin must provide a get_context() method."
        )

    def render(self, template_name=None, context=None, renderer=None):
        renderer = renderer or self.renderer
        template = template_name or self.template_name
        context = context or self.get_context()
        if (
            template == "django/forms/default.html"
            or template == "django/forms/formsets/default.html"
        ):
            warnings.warn(
                DEFAULT_TEMPLATE_DEPRECATION_MSG, RemovedInDjango50Warning, stacklevel=2
            )
        return mark_safe(renderer.render(template, context))

    __str__ = render
    __html__ = render
