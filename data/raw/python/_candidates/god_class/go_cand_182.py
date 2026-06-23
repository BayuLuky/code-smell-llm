class ModelState:
    """
    Represent a Django Model. Don't use the actual Model class as it's not
    designed to have its options changed - instead, mutate this one and then
    render it into a Model as required.

    Note that while you are allowed to mutate .fields, you are not allowed
    to mutate the Field instances inside there themselves - you must instead
    assign new ones, as these are not detached during a clone.
    """

    def __init__(
        self, app_label, name, fields, options=None, bases=None, managers=None
    ):
        self.app_label = app_label
        self.name = name
        self.fields = dict(fields)
        self.options = options or {}
        self.options.setdefault("indexes", [])
        self.options.setdefault("constraints", [])
        self.bases = bases or (models.Model,)
        self.managers = managers or []
        for name, field in self.fields.items():
            # Sanity-check that fields are NOT already bound to a model.
            if hasattr(field, "model"):
                raise ValueError(
                    'ModelState.fields cannot be bound to a model - "%s" is.' % name
                )
            # Sanity-check that relation fields are NOT referring to a model class.
            if field.is_relation and hasattr(field.related_model, "_meta"):
                raise ValueError(
                    'ModelState.fields cannot refer to a model class - "%s.to" does. '
                    "Use a string reference instead." % name
                )
            if field.many_to_many and hasattr(field.remote_field.through, "_meta"):
                raise ValueError(
                    'ModelState.fields cannot refer to a model class - "%s.through" '
                    "does. Use a string reference instead." % name
                )
        # Sanity-check that indexes have their name set.
        for index in self.options["indexes"]:
            if not index.name:
                raise ValueError(
                    "Indexes passed to ModelState require a name attribute. "
                    "%r doesn't have one." % index
                )

    @cached_property
    def name_lower(self):
        return self.name.lower()

    def get_field(self, field_name):
        if field_name == "_order":
            field_name = self.options.get("order_with_respect_to", field_name)
        return self.fields[field_name]

    @classmethod
    def from_model(cls, model, exclude_rels=False):
        """Given a model, return a ModelState representing it."""
        # Deconstruct the fields
        fields = []
        for field in model._meta.local_fields:
            if getattr(field, "remote_field", None) and exclude_rels:
                continue
            if isinstance(field, models.OrderWrt):
                continue
            name = field.name
            try:
                fields.append((name, field.clone()))
            except TypeError as e:
                raise TypeError(
                    "Couldn't reconstruct field %s on %s: %s"
                    % (
                        name,
                        model._meta.label,
                        e,
                    )
                )
        if not exclude_rels:
            for field in model._meta.local_many_to_many:
                name = field.name
                try:
                    fields.append((name, field.clone()))
                except TypeError as e:
                    raise TypeError(
                        "Couldn't reconstruct m2m field %s on %s: %s"
                        % (
                            name,
                            model._meta.object_name,
                            e,
                        )
                    )
        # Extract the options
        options = {}
        for name in DEFAULT_NAMES:
            # Ignore some special options
            if name in ["apps", "app_label"]:
                continue
            elif name in model._meta.original_attrs:
                if name == "unique_together":
                    ut = model._meta.original_attrs["unique_together"]
                    options[name] = set(normalize_together(ut))
                elif name == "index_together":
                    it = model._meta.original_attrs["index_together"]
                    options[name] = set(normalize_together(it))
                elif name == "indexes":
                    indexes = [idx.clone() for idx in model._meta.indexes]
                    for index in indexes:
                        if not index.name:
                            index.set_name_with_model(model)
                    options["indexes"] = indexes
                elif name == "constraints":
                    options["constraints"] = [
                        con.clone() for con in model._meta.constraints
                    ]
                else:
                    options[name] = model._meta.original_attrs[name]
        # If we're ignoring relationships, remove all field-listing model
        # options (that option basically just means "make a stub model")
        if exclude_rels:
            for key in ["unique_together", "index_together", "order_with_respect_to"]:
                if key in options:
                    del options[key]
        # Private fields are ignored, so remove options that refer to them.
        elif options.get("order_with_respect_to") in {
            field.name for field in model._meta.private_fields
        }:
            del options["order_with_respect_to"]

        def flatten_bases(model):
            bases = []
            for base in model.__bases__:
                if hasattr(base, "_meta") and base._meta.abstract:
                    bases.extend(flatten_bases(base))
                else:
                    bases.append(base)
            return bases

        # We can't rely on __mro__ directly because we only want to flatten
        # abstract models and not the whole tree. However by recursing on
        # __bases__ we may end up with duplicates and ordering issues, we
        # therefore discard any duplicates and reorder the bases according
        # to their index in the MRO.
        flattened_bases = sorted(
            set(flatten_bases(model)), key=lambda x: model.__mro__.index(x)
        )

        # Make our record
        bases = tuple(
            (base._meta.label_lower if hasattr(base, "_meta") else base)
            for base in flattened_bases
        )
        # Ensure at least one base inherits from models.Model
        if not any(
            (isinstance(base, str) or issubclass(base, models.Model)) for base in bases
        ):
            bases = (models.Model,)

        managers = []
        manager_names = set()
        default_manager_shim = None
        for manager in model._meta.managers:
            if manager.name in manager_names:
                # Skip overridden managers.
                continue
            elif manager.use_in_migrations:
                # Copy managers usable in migrations.
                new_manager = copy.copy(manager)
                new_manager._set_creation_counter()
            elif manager is model._base_manager or manager is model._default_manager:
                # Shim custom managers used as default and base managers.
                new_manager = models.Manager()
                new_manager.model = manager.model
                new_manager.name = manager.name
                if manager is model._default_manager:
                    default_manager_shim = new_manager
            else:
                continue
            manager_names.add(manager.name)
            managers.append((manager.name, new_manager))

        # Ignore a shimmed default manager called objects if it's the only one.
        if managers == [("objects", default_manager_shim)]:
            managers = []

        # Construct the new ModelState
        return cls(
            model._meta.app_label,
            model._meta.object_name,
            fields,
            options,
            bases,
            managers,
        )

    def construct_managers(self):
        """Deep-clone the managers using deconstruction."""
        # Sort all managers by their creation counter
        sorted_managers = sorted(self.managers, key=lambda v: v[1].creation_counter)
        for mgr_name, manager in sorted_managers:
            as_manager, manager_path, qs_path, args, kwargs = manager.deconstruct()
            if as_manager:
                qs_class = import_string(qs_path)
                yield mgr_name, qs_class.as_manager()
            else:
                manager_class = import_string(manager_path)
                yield mgr_name, manager_class(*args, **kwargs)

    def clone(self):
        """Return an exact copy of this ModelState."""
        return self.__class__(
            app_label=self.app_label,
            name=self.name,
            fields=dict(self.fields),
            # Since options are shallow-copied here, operations such as
            # AddIndex must replace their option (e.g 'indexes') rather
            # than mutating it.
            options=dict(self.options),
            bases=self.bases,
            managers=list(self.managers),
        )

    def render(self, apps):
        """Create a Model object from our current state into the given apps."""
        # First, make a Meta object
        meta_contents = {"app_label": self.app_label, "apps": apps, **self.options}
        meta = type("Meta", (), meta_contents)
        # Then, work out our bases
        try:
            bases = tuple(
                (apps.get_model(base) if isinstance(base, str) else base)
                for base in self.bases
            )
        except LookupError:
            raise InvalidBasesError(
                "Cannot resolve one or more bases from %r" % (self.bases,)
            )
        # Clone fields for the body, add other bits.
        body = {name: field.clone() for name, field in self.fields.items()}
        body["Meta"] = meta
        body["__module__"] = "__fake__"

        # Restore managers
        body.update(self.construct_managers())
        # Then, make a Model object (apps.register_model is called in __new__)
        return type(self.name, bases, body)

    def get_index_by_name(self, name):
        for index in self.options["indexes"]:
            if index.name == name:
                return index
        raise ValueError("No index named %s on model %s" % (name, self.name))

    def get_constraint_by_name(self, name):
        for constraint in self.options["constraints"]:
            if constraint.name == name:
                return constraint
        raise ValueError("No constraint named %s on model %s" % (name, self.name))

    def __repr__(self):
        return "<%s: '%s.%s'>" % (self.__class__.__name__, self.app_label, self.name)

    def __eq__(self, other):
        return (
            (self.app_label == other.app_label)
            and (self.name == other.name)
            and (len(self.fields) == len(other.fields))
            and all(
                k1 == k2 and f1.deconstruct()[1:] == f2.deconstruct()[1:]
                for (k1, f1), (k2, f2) in zip(
                    sorted(self.fields.items()),
                    sorted(other.fields.items()),
                )
            )
            and (self.options == other.options)
            and (self.bases == other.bases)
            and (self.managers == other.managers)
        )
