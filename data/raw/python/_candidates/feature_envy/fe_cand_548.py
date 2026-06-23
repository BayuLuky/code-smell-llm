def reconstruction_error(self):
    """Compute the reconstruction error for the embedding.

    Returns
    -------
    reconstruction_error : float
        Reconstruction error.

    Notes
    -----
    The cost function of an isomap embedding is

    ``E = frobenius_norm[K(D) - K(D_fit)] / n_samples``

    Where D is the matrix of distances for the input data X,
    D_fit is the matrix of distances for the output embedding X_fit,
    and K is the isomap kernel:

    ``K(D) = -0.5 * (I - 1/n_samples) * D^2 * (I - 1/n_samples)``
    """
    G = -0.5 * self.dist_matrix_**2
    G_center = KernelCenterer().fit_transform(G)
    evals = self.kernel_pca_.eigenvalues_
    return np.sqrt(np.sum(G_center**2) - np.sum(evals**2)) / G.shape[0]
