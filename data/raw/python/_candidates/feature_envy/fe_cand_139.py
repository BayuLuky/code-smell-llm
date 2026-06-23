def recurse(self, node, tree, ax, max_x, max_y, depth=0):
    import matplotlib.pyplot as plt

    kwargs = dict(
        bbox=self.bbox_args.copy(),
        ha="center",
        va="center",
        zorder=100 - 10 * depth,
        xycoords="axes fraction",
        arrowprops=self.arrow_args.copy(),
    )
    kwargs["arrowprops"]["edgecolor"] = plt.rcParams["text.color"]

    if self.fontsize is not None:
        kwargs["fontsize"] = self.fontsize

    # offset things by .5 to center them in plot
    xy = ((node.x + 0.5) / max_x, (max_y - node.y - 0.5) / max_y)

    if self.max_depth is None or depth <= self.max_depth:
        if self.filled:
            kwargs["bbox"]["fc"] = self.get_fill_color(tree, node.tree.node_id)
        else:
            kwargs["bbox"]["fc"] = ax.get_facecolor()

        if node.parent is None:
            # root
            ax.annotate(node.tree.label, xy, **kwargs)
        else:
            xy_parent = (
                (node.parent.x + 0.5) / max_x,
                (max_y - node.parent.y - 0.5) / max_y,
            )
            ax.annotate(node.tree.label, xy_parent, xy, **kwargs)
        for child in node.children:
            self.recurse(child, tree, ax, max_x, max_y, depth=depth + 1)

    else:
        xy_parent = (
            (node.parent.x + 0.5) / max_x,
            (max_y - node.parent.y - 0.5) / max_y,
        )
        kwargs["bbox"]["fc"] = "grey"
        ax.annotate("\n  (...)  \n", xy_parent, xy, **kwargs)
