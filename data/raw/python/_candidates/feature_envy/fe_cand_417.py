def merge(*lists):
    """
    Merge lists while trying to keep the relative order of the elements.
    Warn if the lists have the same elements in a different relative order.

    For static assets it can be important to have them included in the DOM
    in a certain order. In JavaScript you may not be able to reference a
    global or in CSS you might want to override a style.
    """
    dependency_graph = defaultdict(set)
    all_items = OrderedSet()
    for list_ in filter(None, lists):
        head = list_[0]
        # The first items depend on nothing but have to be part of the
        # dependency graph to be included in the result.
        dependency_graph.setdefault(head, set())
        for item in list_:
            all_items.add(item)
            # No self dependencies
            if head != item:
                dependency_graph[item].add(head)
            head = item
    try:
        return stable_topological_sort(all_items, dependency_graph)
    except CyclicDependencyError:
        warnings.warn(
            "Detected duplicate Media files in an opposite order: {}".format(
                ", ".join(repr(list_) for list_ in lists)
            ),
            MediaOrderConflictWarning,
        )
        return list(all_items)
