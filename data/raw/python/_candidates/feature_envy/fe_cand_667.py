def to_list(self):
    """Convert tuple to a list where None is always first."""
    output = []
    if self.none:
        output.append(None)
    if self.nan:
        output.append(np.nan)
    return output
