def field_admin_ordering(self, field, request, model_admin):
    """
    Return the model admin's ordering for related field, if provided.
    """
    related_admin = model_admin.admin_site._registry.get(field.remote_field.model)
    if related_admin is not None:
        return related_admin.get_ordering(request)
    return ()
