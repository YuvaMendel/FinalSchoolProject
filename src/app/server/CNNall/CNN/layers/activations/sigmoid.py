import numpy as np
from ..base import Layer


class Sigmoid(Layer):
    def forward(self, z):
        self.output = 1 / (1 + np.exp(-z))
        return self.output

    def backward(self, output_grad):
        return output_grad * self.output * (1 - self.output)
