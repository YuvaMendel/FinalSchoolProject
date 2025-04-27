import numpy as np
from abc import ABC, abstractmethod

# Loss functions for neural networks


class Loss(ABC):
    def __init__(self):
        self.predictions = None
        self.targets = None

    def forward(self, predictions, targets):
        """Computes the loss value."""
        self.predictions = predictions
        self.targets = targets
        return self._compute_loss()

    def backward(self):
        """Computes the gradient of the loss wrt predictions."""
        return self._compute_grad()

    @abstractmethod
    def _compute_loss(self):
        raise NotImplementedError

    @abstractmethod
    def _compute_grad(self):
        raise NotImplementedError
