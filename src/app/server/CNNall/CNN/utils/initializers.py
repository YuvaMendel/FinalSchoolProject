import numpy as np


def xavier_initializer(shape):
    """
    Xavier initializer for any shape of weights.
    - shape: tuple, the shape of the weight tensor
    """
    if len(shape) == 2:
        # Dense layer: (out_features, in_features)
        fan_in, fan_out = shape[1], shape[0]
    elif len(shape) == 4:
        # Conv2D: (out_channels, in_channels, kernel_height, kernel_width)
        fan_in = shape[1] * shape[2] * shape[3]
        fan_out = shape[0] * shape[2] * shape[3]
    else:
        raise ValueError(f"Unsupported shape for Xavier initialization: {shape}")

    limit = np.sqrt(6 / (fan_in + fan_out))
    return np.random.uniform(-limit, limit, size=shape)
