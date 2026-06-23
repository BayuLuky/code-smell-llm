def render_to_response(self, context, **response_kwargs):
    def indent(s):
        return s.replace("\n", "\n  ")

    template = Engine().from_string(js_catalog_template)
    context["catalog_str"] = (
        indent(json.dumps(context["catalog"], sort_keys=True, indent=2))
        if context["catalog"]
        else None
    )
    context["formats_str"] = indent(
        json.dumps(context["formats"], sort_keys=True, indent=2)
    )

    return HttpResponse(
        template.render(Context(context)), 'text/javascript; charset="utf-8"'
    )
