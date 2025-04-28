import numpy as np
from losses import Loss


class CategoricalCrossEntropy(Loss):
    def __init__(self):
        super().__init__()

    def _compute_loss(self):
        # add epsilon to avoid log(0)
        return -np.sum(self.targets * np.log(self.predictions + 1e-8)) / self.targets.shape[0]

    def _compute_grad(self):
        # assumes predicted already passed through softmax
        return self.predictions - self.targets
