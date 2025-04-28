import numpy as np


def xavier_initializer(n_in, n_out):
    """Static method to initialize a weights matrix for a layer using Xavier initialization.
       - n_in: Number of neurons in the previous layer.
       - n_out: Number of neurons in the current layer.
    """
    limit = np.sqrt(6 / (n_in + n_out))
    weights = np.random.uniform(-limit, limit, (n_in, n_out))
    return weights
