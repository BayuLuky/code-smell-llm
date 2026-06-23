def _compute_inverse_components(self):
    """Compute the pseudo-inverse of the (densified) components."""
    components = self.components_
    if sp.issparse(components):
        components = components.toarray()
    return linalg.pinv(components, check_finite=False)
