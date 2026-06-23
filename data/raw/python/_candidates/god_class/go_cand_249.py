class Serializer(base.Serializer):
    """Serialize a QuerySet to XML."""

    def indent(self, level):
        if self.options.get("indent") is not None:
            self.xml.ignorableWhitespace(
                "\n" + " " * self.options.get("indent") * level
            )

    def start_serialization(self):
        """
        Start serialization -- open the XML document and the root element.
        """
        self.xml = SimplerXMLGenerator(
            self.stream, self.options.get("encoding", settings.DEFAULT_CHARSET)
        )
        self.xml.startDocument()
        self.xml.startElement("django-objects", {"version": "1.0"})

    def end_serialization(self):
        """
        End serialization -- end the document.
        """
        self.indent(0)
        self.xml.endElement("django-objects")
        self.xml.endDocument()

    def start_object(self, obj):
        """
        Called as each object is handled.
        """
        if not hasattr(obj, "_meta"):
            raise base.SerializationError(
                "Non-model object (%s) encountered during serialization" % type(obj)
            )

        self.indent(1)
        attrs = {"model": str(obj._meta)}
        if not self.use_natural_primary_keys or not hasattr(obj, "natural_key"):
            obj_pk = obj.pk
            if obj_pk is not None:
                attrs["pk"] = str(obj_pk)

        self.xml.startElement("object", attrs)

    def end_object(self, obj):
        """
        Called after handling all fields for an object.
        """
        self.indent(1)
        self.xml.endElement("object")

    def handle_field(self, obj, field):
        """
        Handle each field on an object (except for ForeignKeys and
        ManyToManyFields).
        """
        self.indent(2)
        self.xml.startElement(
            "field",
            {
                "name": field.name,
                "type": field.get_internal_type(),
            },
        )

        # Get a "string version" of the object's data.
        if getattr(obj, field.name) is not None:
            value = field.value_to_string(obj)
            if field.get_internal_type() == "JSONField":
                # Dump value since JSONField.value_to_string() doesn't output
                # strings.
                value = json.dumps(value, cls=field.encoder)
            try:
                self.xml.characters(value)
            except UnserializableContentError:
                raise ValueError(
                    "%s.%s (pk:%s) contains unserializable characters"
                    % (obj.__class__.__name__, field.name, obj.pk)
                )
        else:
            self.xml.addQuickElement("None")

        self.xml.endElement("field")

    def handle_fk_field(self, obj, field):
        """
        Handle a ForeignKey (they need to be treated slightly
        differently from regular fields).
        """
        self._start_relational_field(field)
        related_att = getattr(obj, field.get_attname())
        if related_att is not None:
            if self.use_natural_foreign_keys and hasattr(
                field.remote_field.model, "natural_key"
            ):
                related = getattr(obj, field.name)
                # If related object has a natural key, use it
                related = related.natural_key()
                # Iterable natural keys are rolled out as subelements
                for key_value in related:
                    self.xml.startElement("natural", {})
                    self.xml.characters(str(key_value))
                    self.xml.endElement("natural")
            else:
                self.xml.characters(str(related_att))
        else:
            self.xml.addQuickElement("None")
        self.xml.endElement("field")

    def handle_m2m_field(self, obj, field):
        """
        Handle a ManyToManyField. Related objects are only serialized as
        references to the object's PK (i.e. the related *data* is not dumped,
        just the relation).
        """
        if field.remote_field.through._meta.auto_created:
            self._start_relational_field(field)
            if self.use_natural_foreign_keys and hasattr(
                field.remote_field.model, "natural_key"
            ):
                # If the objects in the m2m have a natural key, use it
                def handle_m2m(value):
                    natural = value.natural_key()
                    # Iterable natural keys are rolled out as subelements
                    self.xml.startElement("object", {})
                    for key_value in natural:
                        self.xml.startElement("natural", {})
                        self.xml.characters(str(key_value))
                        self.xml.endElement("natural")
                    self.xml.endElement("object")

                def queryset_iterator(obj, field):
                    return getattr(obj, field.name).iterator()

            else:

                def handle_m2m(value):
                    self.xml.addQuickElement("object", attrs={"pk": str(value.pk)})

                def queryset_iterator(obj, field):
                    return (
                        getattr(obj, field.name)
                        .select_related(None)
                        .only("pk")
                        .iterator()
                    )

            m2m_iter = getattr(obj, "_prefetched_objects_cache", {}).get(
                field.name,
                queryset_iterator(obj, field),
            )
            for relobj in m2m_iter:
                handle_m2m(relobj)

            self.xml.endElement("field")

    def _start_relational_field(self, field):
        """Output the <field> element for relational fields."""
        self.indent(2)
        self.xml.startElement(
            "field",
            {
                "name": field.name,
                "rel": field.remote_field.__class__.__name__,
                "to": str(field.remote_field.model._meta),
            },
        )
