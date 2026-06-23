class ManyRelatedManager(superclass, AltersData):
    def __init__(self, instance=None):
        super().__init__()

        self.instance = instance

        if not reverse:
            self.model = rel.model
            self.query_field_name = rel.field.related_query_name()
            self.prefetch_cache_name = rel.field.name
            self.source_field_name = rel.field.m2m_field_name()
            self.target_field_name = rel.field.m2m_reverse_field_name()
            self.symmetrical = rel.symmetrical
        else:
            self.model = rel.related_model
            self.query_field_name = rel.field.name
            self.prefetch_cache_name = rel.field.related_query_name()
            self.source_field_name = rel.field.m2m_reverse_field_name()
            self.target_field_name = rel.field.m2m_field_name()
            self.symmetrical = False

        self.through = rel.through
        self.reverse = reverse

        self.source_field = self.through._meta.get_field(self.source_field_name)
        self.target_field = self.through._meta.get_field(self.target_field_name)

        self.core_filters = {}
        self.pk_field_names = {}
        for lh_field, rh_field in self.source_field.related_fields:
            core_filter_key = "%s__%s" % (self.query_field_name, rh_field.name)
            self.core_filters[core_filter_key] = getattr(instance, rh_field.attname)
            self.pk_field_names[lh_field.name] = rh_field.name

        self.related_val = self.source_field.get_foreign_related_value(instance)
        if None in self.related_val:
            raise ValueError(
                '"%r" needs to have a value for field "%s" before '
                "this many-to-many relationship can be used."
                % (instance, self.pk_field_names[self.source_field_name])
            )
        # Even if this relation is not to pk, we require still pk value.
        # The wish is that the instance has been already saved to DB,
        # although having a pk value isn't a guarantee of that.
        if instance.pk is None:
            raise ValueError(
                "%r instance needs to have a primary key value before "
                "a many-to-many relationship can be used."
                % instance.__class__.__name__
            )

    def __call__(self, *, manager):
        manager = getattr(self.model, manager)
        manager_class = create_forward_many_to_many_manager(
            manager.__class__, rel, reverse
        )
        return manager_class(instance=self.instance)

    do_not_call_in_templates = True

    def _build_remove_filters(self, removed_vals):
        filters = Q.create([(self.source_field_name, self.related_val)])
        # No need to add a subquery condition if removed_vals is a QuerySet without
        # filters.
        removed_vals_filters = (
            not isinstance(removed_vals, QuerySet) or removed_vals._has_filters()
        )
        if removed_vals_filters:
            filters &= Q.create([(f"{self.target_field_name}__in", removed_vals)])
        if self.symmetrical:
            symmetrical_filters = Q.create(
                [(self.target_field_name, self.related_val)]
            )
            if removed_vals_filters:
                symmetrical_filters &= Q.create(
                    [(f"{self.source_field_name}__in", removed_vals)]
                )
            filters |= symmetrical_filters
        return filters

    def _apply_rel_filters(self, queryset):
        """
        Filter the queryset for the instance this manager is bound to.
        """
        queryset._add_hints(instance=self.instance)
        if self._db:
            queryset = queryset.using(self._db)
        queryset._defer_next_filter = True
        return queryset._next_is_sticky().filter(**self.core_filters)

    def _remove_prefetched_objects(self):
        try:
            self.instance._prefetched_objects_cache.pop(self.prefetch_cache_name)
        except (AttributeError, KeyError):
            pass  # nothing to clear from cache

    def get_queryset(self):
        try:
            return self.instance._prefetched_objects_cache[self.prefetch_cache_name]
        except (AttributeError, KeyError):
            queryset = super().get_queryset()
            return self._apply_rel_filters(queryset)

    def get_prefetch_queryset(self, instances, queryset=None):
        if queryset is None:
            queryset = super().get_queryset()

        queryset._add_hints(instance=instances[0])
        queryset = queryset.using(queryset._db or self._db)
        queryset = _filter_prefetch_queryset(
            queryset._next_is_sticky(), self.query_field_name, instances
        )

        # M2M: need to annotate the query in order to get the primary model
        # that the secondary model was actually related to. We know that
        # there will already be a join on the join table, so we can just add
        # the select.

        # For non-autocreated 'through' models, can't assume we are
        # dealing with PK values.
        fk = self.through._meta.get_field(self.source_field_name)
        join_table = fk.model._meta.db_table
        connection = connections[queryset.db]
        qn = connection.ops.quote_name
        queryset = queryset.extra(
            select={
                "_prefetch_related_val_%s"
                % f.attname: "%s.%s"
                % (qn(join_table), qn(f.column))
                for f in fk.local_related_fields
            }
        )
        return (
            queryset,
            lambda result: tuple(
                getattr(result, "_prefetch_related_val_%s" % f.attname)
                for f in fk.local_related_fields
            ),
            lambda inst: tuple(
                f.get_db_prep_value(getattr(inst, f.attname), connection)
                for f in fk.foreign_related_fields
            ),
            False,
            self.prefetch_cache_name,
            False,
        )

    def add(self, *objs, through_defaults=None):
        self._remove_prefetched_objects()
        db = router.db_for_write(self.through, instance=self.instance)
        with transaction.atomic(using=db, savepoint=False):
            self._add_items(
                self.source_field_name,
                self.target_field_name,
                *objs,
                through_defaults=through_defaults,
            )
            # If this is a symmetrical m2m relation to self, add the mirror
            # entry in the m2m table.
            if self.symmetrical:
                self._add_items(
                    self.target_field_name,
                    self.source_field_name,
                    *objs,
                    through_defaults=through_defaults,
                )

    add.alters_data = True

    async def aadd(self, *objs, through_defaults=None):
        return await sync_to_async(self.add)(
            *objs, through_defaults=through_defaults
        )

    aadd.alters_data = True

    def remove(self, *objs):
        self._remove_prefetched_objects()
        self._remove_items(self.source_field_name, self.target_field_name, *objs)

    remove.alters_data = True

    async def aremove(self, *objs):
        return await sync_to_async(self.remove)(*objs)

    aremove.alters_data = True

    def clear(self):
        db = router.db_for_write(self.through, instance=self.instance)
        with transaction.atomic(using=db, savepoint=False):
            signals.m2m_changed.send(
                sender=self.through,
                action="pre_clear",
                instance=self.instance,
                reverse=self.reverse,
                model=self.model,
                pk_set=None,
                using=db,
            )
            self._remove_prefetched_objects()
            filters = self._build_remove_filters(super().get_queryset().using(db))
            self.through._default_manager.using(db).filter(filters).delete()

            signals.m2m_changed.send(
                sender=self.through,
                action="post_clear",
                instance=self.instance,
                reverse=self.reverse,
                model=self.model,
                pk_set=None,
                using=db,
            )

    clear.alters_data = True

    async def aclear(self):
        return await sync_to_async(self.clear)()

    aclear.alters_data = True

    def set(self, objs, *, clear=False, through_defaults=None):
        # Force evaluation of `objs` in case it's a queryset whose value
        # could be affected by `manager.clear()`. Refs #19816.
        objs = tuple(objs)

        db = router.db_for_write(self.through, instance=self.instance)
        with transaction.atomic(using=db, savepoint=False):
            if clear:
                self.clear()
                self.add(*objs, through_defaults=through_defaults)
            else:
                old_ids = set(
                    self.using(db).values_list(
                        self.target_field.target_field.attname, flat=True
                    )
                )

                new_objs = []
                for obj in objs:
                    fk_val = (
                        self.target_field.get_foreign_related_value(obj)[0]
                        if isinstance(obj, self.model)
                        else self.target_field.get_prep_value(obj)
                    )
                    if fk_val in old_ids:
                        old_ids.remove(fk_val)
                    else:
                        new_objs.append(obj)

                self.remove(*old_ids)
                self.add(*new_objs, through_defaults=through_defaults)

    set.alters_data = True

    async def aset(self, objs, *, clear=False, through_defaults=None):
        return await sync_to_async(self.set)(
            objs=objs, clear=clear, through_defaults=through_defaults
        )

    aset.alters_data = True

    def create(self, *, through_defaults=None, **kwargs):
        db = router.db_for_write(self.instance.__class__, instance=self.instance)
        new_obj = super(ManyRelatedManager, self.db_manager(db)).create(**kwargs)
        self.add(new_obj, through_defaults=through_defaults)
        return new_obj

    create.alters_data = True

    async def acreate(self, *, through_defaults=None, **kwargs):
        return await sync_to_async(self.create)(
            through_defaults=through_defaults, **kwargs
        )

    acreate.alters_data = True

    def get_or_create(self, *, through_defaults=None, **kwargs):
        db = router.db_for_write(self.instance.__class__, instance=self.instance)
        obj, created = super(ManyRelatedManager, self.db_manager(db)).get_or_create(
            **kwargs
        )
        # We only need to add() if created because if we got an object back
        # from get() then the relationship already exists.
        if created:
            self.add(obj, through_defaults=through_defaults)
        return obj, created

    get_or_create.alters_data = True

    async def aget_or_create(self, *, through_defaults=None, **kwargs):
        return await sync_to_async(self.get_or_create)(
            through_defaults=through_defaults, **kwargs
        )

    aget_or_create.alters_data = True

    def update_or_create(self, *, through_defaults=None, **kwargs):
        db = router.db_for_write(self.instance.__class__, instance=self.instance)
        obj, created = super(
            ManyRelatedManager, self.db_manager(db)
        ).update_or_create(**kwargs)
        # We only need to add() if created because if we got an object back
        # from get() then the relationship already exists.
        if created:
            self.add(obj, through_defaults=through_defaults)
        return obj, created

    update_or_create.alters_data = True

    async def aupdate_or_create(self, *, through_defaults=None, **kwargs):
        return await sync_to_async(self.update_or_create)(
            through_defaults=through_defaults, **kwargs
        )

    aupdate_or_create.alters_data = True

    def _get_target_ids(self, target_field_name, objs):
        """
        Return the set of ids of `objs` that the target field references.
        """
        from django.db.models import Model

        target_ids = set()
        target_field = self.through._meta.get_field(target_field_name)
        for obj in objs:
            if isinstance(obj, self.model):
                if not router.allow_relation(obj, self.instance):
                    raise ValueError(
                        'Cannot add "%r": instance is on database "%s", '
                        'value is on database "%s"'
                        % (obj, self.instance._state.db, obj._state.db)
                    )
                target_id = target_field.get_foreign_related_value(obj)[0]
                if target_id is None:
                    raise ValueError(
                        'Cannot add "%r": the value for field "%s" is None'
                        % (obj, target_field_name)
                    )
                target_ids.add(target_id)
            elif isinstance(obj, Model):
                raise TypeError(
                    "'%s' instance expected, got %r"
                    % (self.model._meta.object_name, obj)
                )
            else:
                target_ids.add(target_field.get_prep_value(obj))
        return target_ids

    def _get_missing_target_ids(
        self, source_field_name, target_field_name, db, target_ids
    ):
        """
        Return the subset of ids of `objs` that aren't already assigned to
        this relationship.
        """
        vals = (
            self.through._default_manager.using(db)
            .values_list(target_field_name, flat=True)
            .filter(
                **{
                    source_field_name: self.related_val[0],
                    "%s__in" % target_field_name: target_ids,
                }
            )
        )
        return target_ids.difference(vals)

    def _get_add_plan(self, db, source_field_name):
        """
        Return a boolean triple of the way the add should be performed.

        The first element is whether or not bulk_create(ignore_conflicts)
        can be used, the second whether or not signals must be sent, and
        the third element is whether or not the immediate bulk insertion
        with conflicts ignored can be performed.
        """
        # Conflicts can be ignored when the intermediary model is
        # auto-created as the only possible collision is on the
        # (source_id, target_id) tuple. The same assertion doesn't hold for
        # user-defined intermediary models as they could have other fields
        # causing conflicts which must be surfaced.
        can_ignore_conflicts = (
            self.through._meta.auto_created is not False
            and connections[db].features.supports_ignore_conflicts
        )
        # Don't send the signal when inserting duplicate data row
        # for symmetrical reverse entries.
        must_send_signals = (
            self.reverse or source_field_name == self.source_field_name
        ) and (signals.m2m_changed.has_listeners(self.through))
        # Fast addition through bulk insertion can only be performed
        # if no m2m_changed listeners are connected for self.through
        # as they require the added set of ids to be provided via
        # pk_set.
        return (
            can_ignore_conflicts,
            must_send_signals,
            (can_ignore_conflicts and not must_send_signals),
        )

    def _add_items(
        self, source_field_name, target_field_name, *objs, through_defaults=None
    ):
        # source_field_name: the PK fieldname in join table for the source object
        # target_field_name: the PK fieldname in join table for the target object
        # *objs - objects to add. Either object instances, or primary keys
        # of object instances.
        if not objs:
            return

        through_defaults = dict(resolve_callables(through_defaults or {}))
        target_ids = self._get_target_ids(target_field_name, objs)
        db = router.db_for_write(self.through, instance=self.instance)
        can_ignore_conflicts, must_send_signals, can_fast_add = self._get_add_plan(
            db, source_field_name
        )
        if can_fast_add:
            self.through._default_manager.using(db).bulk_create(
                [
                    self.through(
                        **{
                            "%s_id" % source_field_name: self.related_val[0],
                            "%s_id" % target_field_name: target_id,
                        }
                    )
                    for target_id in target_ids
                ],
                ignore_conflicts=True,
            )
            return

        missing_target_ids = self._get_missing_target_ids(
            source_field_name, target_field_name, db, target_ids
        )
        with transaction.atomic(using=db, savepoint=False):
            if must_send_signals:
                signals.m2m_changed.send(
                    sender=self.through,
                    action="pre_add",
                    instance=self.instance,
                    reverse=self.reverse,
                    model=self.model,
                    pk_set=missing_target_ids,
                    using=db,
                )
            # Add the ones that aren't there already.
            self.through._default_manager.using(db).bulk_create(
                [
                    self.through(
                        **through_defaults,
                        **{
                            "%s_id" % source_field_name: self.related_val[0],
                            "%s_id" % target_field_name: target_id,
                        },
                    )
                    for target_id in missing_target_ids
                ],
                ignore_conflicts=can_ignore_conflicts,
            )

            if must_send_signals:
                signals.m2m_changed.send(
                    sender=self.through,
                    action="post_add",
                    instance=self.instance,
                    reverse=self.reverse,
                    model=self.model,
                    pk_set=missing_target_ids,
                    using=db,
                )

    def _remove_items(self, source_field_name, target_field_name, *objs):
        # source_field_name: the PK colname in join table for the source object
        # target_field_name: the PK colname in join table for the target object
        # *objs - objects to remove. Either object instances, or primary
        # keys of object instances.
        if not objs:
            return

        # Check that all the objects are of the right type
        old_ids = set()
        for obj in objs:
            if isinstance(obj, self.model):
                fk_val = self.target_field.get_foreign_related_value(obj)[0]
                old_ids.add(fk_val)
            else:
                old_ids.add(obj)

        db = router.db_for_write(self.through, instance=self.instance)
        with transaction.atomic(using=db, savepoint=False):
            # Send a signal to the other end if need be.
            signals.m2m_changed.send(
                sender=self.through,
                action="pre_remove",
                instance=self.instance,
                reverse=self.reverse,
                model=self.model,
                pk_set=old_ids,
                using=db,
            )
            target_model_qs = super().get_queryset()
            if target_model_qs._has_filters():
                old_vals = target_model_qs.using(db).filter(
                    **{"%s__in" % self.target_field.target_field.attname: old_ids}
                )
            else:
                old_vals = old_ids
            filters = self._build_remove_filters(old_vals)
            self.through._default_manager.using(db).filter(filters).delete()

            signals.m2m_changed.send(
                sender=self.through,
                action="post_remove",
                instance=self.instance,
                reverse=self.reverse,
                model=self.model,
                pk_set=old_ids,
                using=db,
            )
