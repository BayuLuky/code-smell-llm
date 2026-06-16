def get_field_type(self, connection, table_name, row):
    """
    Given the database connection, the table name, and the cursor row
    description, this routine will return the given field type name, as
    well as any additional keyword parameters and notes for the field.
    """
    field_params = {}
    field_notes = []

    try:
        field_type = connection.introspection.get_field_type(row.type_code, row)
    except KeyError:
        field_type = "TextField"
        field_notes.append("This field type is a guess.")

    # Add max_length for all CharFields.
    if field_type == "CharField" and row.display_size:
        if (size := int(row.display_size)) and size > 0:
            field_params["max_length"] = size

    if field_type in {"CharField", "TextField"} and row.collation:
        field_params["db_collation"] = row.collation

    if field_type == "DecimalField":
        if row.precision is None or row.scale is None:
            field_notes.append(
                "max_digits and decimal_places have been guessed, as this "
                "database handles decimal fields as float"
            )
            field_params["max_digits"] = (
                row.precision if row.precision is not None else 10
            )
            field_params["decimal_places"] = (
                row.scale if row.scale is not None else 5
            )
        else:
            field_params["max_digits"] = row.precision
            field_params["decimal_places"] = row.scale

    return field_type, field_params, field_notes
