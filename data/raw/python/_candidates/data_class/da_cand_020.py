class TreeNode:
    """Tree Node class used in TreeGrower.

    This isn't used for prediction purposes, only for training (see
    TreePredictor).

    Parameters
    ----------
    depth : int
        The depth of the node, i.e. its distance from the root.
    sample_indices : ndarray of shape (n_samples_at_node,), dtype=np.uint32
        The indices of the samples at the node.
    sum_gradients : float
        The sum of the gradients of the samples at the node.
    sum_hessians : float
        The sum of the hessians of the samples at the node.

    Attributes
    ----------
    depth : int
        The depth of the node, i.e. its distance from the root.
    sample_indices : ndarray of shape (n_samples_at_node,), dtype=np.uint32
        The indices of the samples at the node.
    sum_gradients : float
        The sum of the gradients of the samples at the node.
    sum_hessians : float
        The sum of the hessians of the samples at the node.
    split_info : SplitInfo or None
        The result of the split evaluation.
    is_leaf : bool
        True if node is a leaf
    left_child : TreeNode or None
        The left child of the node. None for leaves.
    right_child : TreeNode or None
        The right child of the node. None for leaves.
    value : float or None
        The value of the leaf, as computed in finalize_leaf(). None for
        non-leaf nodes.
    partition_start : int
        start position of the node's sample_indices in splitter.partition.
    partition_stop : int
        stop position of the node's sample_indices in splitter.partition.
    allowed_features : None or ndarray, dtype=int
        Indices of features allowed to split for children.
    interaction_cst_indices : None or list of ints
        Indices of the interaction sets that have to be applied on splits of
        child nodes. The fewer sets the stronger the constraint as fewer sets
        contain fewer features.
    children_lower_bound : float
    children_upper_bound : float
    """

    split_info = None
    left_child = None
    right_child = None
    histograms = None

    # start and stop indices of the node in the splitter.partition
    # array. Concretely,
    # self.sample_indices = view(self.splitter.partition[start:stop])
    # Please see the comments about splitter.partition and
    # splitter.split_indices for more info about this design.
    # These 2 attributes are only used in _update_raw_prediction, because we
    # need to iterate over the leaves and I don't know how to efficiently
    # store the sample_indices views because they're all of different sizes.
    partition_start = 0
    partition_stop = 0

    def __init__(self, depth, sample_indices, sum_gradients, sum_hessians, value=None):
        self.depth = depth
        self.sample_indices = sample_indices
        self.n_samples = sample_indices.shape[0]
        self.sum_gradients = sum_gradients
        self.sum_hessians = sum_hessians
        self.value = value
        self.is_leaf = False
        self.allowed_features = None
        self.interaction_cst_indices = None
        self.set_children_bounds(float("-inf"), float("+inf"))

    def set_children_bounds(self, lower, upper):
        """Set children values bounds to respect monotonic constraints."""

        # These are bounds for the node's *children* values, not the node's
        # value. The bounds are used in the splitter when considering potential
        # left and right child.
        self.children_lower_bound = lower
        self.children_upper_bound = upper

    def __lt__(self, other_node):
        """Comparison for priority queue.

        Nodes with high gain are higher priority than nodes with low gain.

        heapq.heappush only need the '<' operator.
        heapq.heappop take the smallest item first (smaller is higher
        priority).

        Parameters
        ----------
        other_node : TreeNode
            The node to compare with.
        """
        return self.split_info.gain > other_node.split_info.gain
