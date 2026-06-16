def get_fill_color(self, tree, node_id):
    # Fetch appropriate color for node
    if "rgb" not in self.colors:
        # Initialize colors and bounds if required
        self.colors["rgb"] = _color_brew(tree.n_classes[0])
        if tree.n_outputs != 1:
            # Find max and min impurities for multi-output
            self.colors["bounds"] = (np.min(-tree.impurity), np.max(-tree.impurity))
        elif tree.n_classes[0] == 1 and len(np.unique(tree.value)) != 1:
            # Find max and min values in leaf nodes for regression
            self.colors["bounds"] = (np.min(tree.value), np.max(tree.value))
    if tree.n_outputs == 1:
        node_val = tree.value[node_id][0, :]
        if (
            tree.n_classes[0] == 1
            and isinstance(node_val, Iterable)
            and self.colors["bounds"] is not None
        ):
            # Unpack the float only for the regression tree case.
            # Classification tree requires an Iterable in `get_color`.
            node_val = node_val.item()
    else:
        # If multi-output color node by impurity
        node_val = -tree.impurity[node_id]
    return self.get_color(node_val)
