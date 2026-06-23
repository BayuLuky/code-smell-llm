class ReverseOneToOneDescriptor:
    """
    Accessor to the related object on the reverse side of a one-to-one
    relation.

    In the example::

        class Restaurant(Model):
            place = OneToOneField(Place, related_name='restaurant')

    ``Place.restaurant`` is a ``ReverseOneToOneDescriptor`` instance.
    """

    def __init__(self, related):
        # Following the example above, `related` is an instance of OneToOneRel
        # which represents the reverse restaurant field (place.restaurant).
        self.related = related

    @cached_property
    def RelatedObjectDoesNotExist(self):
        # The exception isn't created at initialization time for the sake of
        # consistency with `ForwardManyToOneDescriptor`.
        return type(
            "RelatedObjectDoesNotExist",
            (self.related.related_model.DoesNotExist, AttributeError),
            {
                "__module__": self.related.model.__module__,
                "__qualname__": "%s.%s.RelatedObjectDoesNotExist"
                % (
                    self.related.model.__qualname__,
                    self.related.name,
                ),
            },
        )

    def is_cached(self, instance):
        return self.related.is_cached(instance)

    def get_queryset(self, **hints):
        return self.related.related_model._base_manager.db_manager(hints=hints).all()

    def get_prefetch_queryset(self, instances, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        queryset._add_hints(instance=instances[0])

        rel_obj_attr = self.related.field.get_local_related_value
        instance_attr = self.related.field.get_foreign_related_value
        instances_dict = {instance_attr(inst): inst for inst in instances}
        query = {"%s__in" % self.related.field.name: instances}
        queryset = queryset.filter(**query)

        # Since we're going to assign directly in the cache,
        # we must manage the reverse relation cache manually.
        for rel_obj in queryset:
            instance = instances_dict[rel_obj_attr(rel_obj)]
            self.related.field.set_cached_value(rel_obj, instance)
        return (
            queryset,
            rel_obj_attr,
            instance_attr,
            True,
            self.related.get_cache_name(),
            False,
        )

    def __get__(self, instance, cls=None):
        """
        Get the related instance through the reverse relation.

        With the example above, when getting ``place.restaurant``:

        - ``self`` is the descriptor managing the ``restaurant`` attribute
        - ``instance`` is the ``place`` instance
        - ``cls`` is the ``Place`` class (unused)

        Keep in mind that ``Restaurant`` holds the foreign key to ``Place``.
        """
        if instance is None:
            return self

        # The related instance is loaded from the database and then cached
        # by the field on the model instance state. It can also be pre-cached
        # by the forward accessor (ForwardManyToOneDescriptor).
        try:
            rel_obj = self.related.get_cached_value(instance)
        except KeyError:
            related_pk = instance.pk
            if related_pk is None:
                rel_obj = None
            else:
                filter_args = self.related.field.get_forward_related_filter(instance)
                try:
                    rel_obj = self.get_queryset(instance=instance).get(**filter_args)
                except self.related.related_model.DoesNotExist:
                    rel_obj = None
                else:
                    # Set the forward accessor cache on the related object to
                    # the current instance to avoid an extra SQL query if it's
                    # accessed later on.
                    self.related.field.set_cached_value(rel_obj, instance)
            self.related.set_cached_value(instance, rel_obj)

        if rel_obj is None:
            raise self.RelatedObjectDoesNotExist(
                "%s has no %s."
                % (instance.__class__.__name__, self.related.get_accessor_name())
            )
        else:
            return rel_obj

    def __set__(self, instance, value):
        """
        Set the related instance through the reverse relation.

        With the example above, when setting ``place.restaurant = restaurant``:

        - ``self`` is the descriptor managing the ``restaurant`` attribute
        - ``instance`` is the ``place`` instance
        - ``value`` is the ``restaurant`` instance on the right of the equal sign

        Keep in mind that ``Restaurant`` holds the foreign key to ``Place``.
        """
        # The similarity of the code below to the code in
        # ForwardManyToOneDescriptor is annoying, but there's a bunch
        # of small differences that would make a common base class convoluted.

        if value is None:
            # Update the cached related instance (if any) & clear the cache.
            # Following the example above, this would be the cached
            # ``restaurant`` instance (if any).
            rel_obj = self.related.get_cached_value(instance, default=None)
            if rel_obj is not None:
                # Remove the ``restaurant`` instance from the ``place``
                # instance cache.
                self.related.delete_cached_value(instance)
                # Set the ``place`` field on the ``restaurant``
                # instance to None.
                setattr(rel_obj, self.related.field.name, None)
        elif not isinstance(value, self.related.related_model):
            # An object must be an instance of the related class.
            raise ValueError(
                'Cannot assign "%r": "%s.%s" must be a "%s" instance.'
                % (
                    value,
                    instance._meta.object_name,
                    self.related.get_accessor_name(),
                    self.related.related_model._meta.object_name,
                )
            )
        else:
            if instance._state.db is None:
                instance._state.db = router.db_for_write(
                    instance.__class__, instance=value
                )
            if value._state.db is None:
                value._state.db = router.db_for_write(
                    value.__class__, instance=instance
                )
            if not router.allow_relation(value, instance):
                raise ValueError(
                    'Cannot assign "%r": the current database router prevents this '
                    "relation." % value
                )

            related_pk = tuple(
                getattr(instance, field.attname)
                for field in self.related.field.foreign_related_fields
            )
            # Set the value of the related field to the value of the related
            # object's related field.
            for index, field in enumerate(self.related.field.local_related_fields):
                setattr(value, field.attname, related_pk[index])

            # Set the related instance cache used by __get__ to avoid an SQL query
            # when accessing the attribute we just set.
            self.related.set_cached_value(instance, value)

            # Set the forward accessor cache on the related object to the current
            # instance to avoid an extra SQL query if it's accessed later on.
            self.related.field.set_cached_value(value, instance)

    def __reduce__(self):
        # Same purpose as ForwardManyToOneDescriptor.__reduce__().
        return getattr, (self.related.model, self.related.name)
