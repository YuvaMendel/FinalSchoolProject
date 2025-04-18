import numpy as np
from base import LossFunction


class MeanSquaredError(LossFunction):
    def __call__(self, predicted, target):
        return np.mean((predicted - target) ** 2)

    def derivative(self, predicted, target):
        return 2 * (predicted - target) / target.size
