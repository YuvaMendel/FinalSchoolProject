import numpy as np
from base import LossFunction


class CategoricalCrossentropy(LossFunction):
    def __call__(self, predicted, target):
        # add epsilon to avoid log(0)
        return -np.sum(target * np.log(predicted + 1e-8)) / target.shape[0]

    def derivative(self, predicted, target):
        # assumes predicted already passed through softmax
        return predicted - target
