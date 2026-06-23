class BaseAdminDocsView(TemplateView):
    """
    Base view for admindocs views.
    """

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        if not utils.docutils_is_available:
            # Display an error message for people without docutils
            self.template_name = "admin_doc/missing_docutils.html"
            return self.render_to_response(admin.site.each_context(request))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **{
                **kwargs,
                **admin.site.each_context(self.request),
            }
        )
