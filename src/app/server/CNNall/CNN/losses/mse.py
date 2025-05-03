import numpy as np
from .base import Loss


class MeanSquaredError(Loss):
    def __init__(self):
        super().__init__()

    def _compute_loss(self):
        return np.mean((self.predictions - self.targets) ** 2)

    def _compute_grad(self):
        return 2 * (self.predictions - self.targets) / self.targets.size
