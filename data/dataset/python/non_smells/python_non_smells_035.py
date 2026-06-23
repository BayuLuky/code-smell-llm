def bind_template(self, template):
    if self.template is not None:
        raise RuntimeError("Context is already bound to a template")

    self.template = template
    # Set context processors according to the template engine's settings.
    processors = template.engine.template_context_processors + self._processors
    updates = {}
    for processor in processors:
        updates.update(processor(self.request))
    self.dicts[self._processors_index] = updates

    try:
        yield
    finally:
        self.template = None
        # Unset context processors.
        self.dicts[self._processors_index] = {}
