import numpy as np
from abc import ABC, abstractmethod

# Loss functions for neural networks


class LossFunction(ABC):
    @abstractmethod
    def __call__(self, predicted, target):
        pass

    @abstractmethod
    def derivative(self, predicted, target):
        pass


class MeanSquaredError(LossFunction):
    def __call__(self, predicted, target):
        return np.mean((predicted - target) ** 2)

    def derivative(self, predicted, target):
        return 2 * (predicted - target) / target.size


class CategoricalCrossentropy(LossFunction):
    def __call__(self, predicted, target):
        # add epsilon to avoid log(0)
        return -np.sum(target * np.log(predicted + 1e-8)) / target.shape[0]

    def derivative(self, predicted, target):
        # assumes predicted already passed through softmax
        return predicted - target
