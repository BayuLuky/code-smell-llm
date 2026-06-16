class BaseDeleteView(DeletionMixin, FormMixin, BaseDetailView):
    """
    Base view for deleting an object.

    Using this base class requires subclassing to provide a response mixin.
    """

    form_class = Form

    def __init__(self, *args, **kwargs):
        # RemovedInDjango50Warning.
        if self.__class__.delete is not DeletionMixin.delete:
            warnings.warn(
                f"DeleteView uses FormMixin to handle POST requests. As a "
                f"consequence, any custom deletion logic in "
                f"{self.__class__.__name__}.delete() handler should be moved "
                f"to form_valid().",
                DeleteViewCustomDeleteWarning,
                stacklevel=2,
            )
        super().__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Set self.object before the usual form processing flow.
        # Inlined because having DeletionMixin as the first base, for
        # get_success_url(), makes leveraging super() with ProcessFormView
        # overly complex.
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)
