class Tree:
    def __init__(self, label="", node_id=-1, *children):
        self.label = label
        self.node_id = node_id
        if children:
            self.children = children
        else:
            self.children = []
