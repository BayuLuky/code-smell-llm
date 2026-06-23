def _assert_formset_error_old_api_cases(
    self, formset, form_index, field, errors, msg_prefix
):
    response = mock.Mock(context=[{"formset": TestFormset.invalid()}])
    return (
        ((response, formset, form_index, field, errors), {}),
        ((response, formset, form_index, field, errors, msg_prefix), {}),
        (
            (response, formset, form_index, field, errors),
            {"msg_prefix": msg_prefix},
        ),
        ((response, formset, form_index, field), {"errors": errors}),
        (
            (response, formset, form_index, field),
            {"errors": errors, "msg_prefix": msg_prefix},
        ),
        ((response, formset, form_index), {"field": field, "errors": errors}),
        (
            (response, formset, form_index),
            {"field": field, "errors": errors, "msg_prefix": msg_prefix},
        ),
        (
            (response, formset),
            {"form_index": form_index, "field": field, "errors": errors},
        ),
        (
            (response, formset),
            {
                "form_index": form_index,
                "field": field,
                "errors": errors,
                "msg_prefix": msg_prefix,
            },
        ),
        (
            (response,),
            {
                "formset": formset,
                "form_index": form_index,
                "field": field,
                "errors": errors,
            },
        ),
        (
            (response,),
            {
                "formset": formset,
                "form_index": form_index,
                "field": field,
                "errors": errors,
                "msg_prefix": msg_prefix,
            },
        ),
        (
            (),
            {
                "response": response,
                "formset": formset,
                "form_index": form_index,
                "field": field,
                "errors": errors,
            },
        ),
        (
            (),
            {
                "response": response,
                "formset": formset,
                "form_index": form_index,
                "field": field,
                "errors": errors,
                "msg_prefix": msg_prefix,
            },
        ),
    )
