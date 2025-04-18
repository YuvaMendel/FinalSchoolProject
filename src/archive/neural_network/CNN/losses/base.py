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






