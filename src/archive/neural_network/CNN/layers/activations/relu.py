from layers import Layer
import numpy as np

class ReLU(Layer):
    def forward(self, z):
        self.input = z
        return np.maximum(0, z)

    def backward(self, output_grad):
        return output_grad * (self.input > 0).astype(float)