import numpy as np

from layer import Layer
# Activation functions for neural networks


class Sigmoid(Layer):
    def forward(self, z):
        self.output = 1 / (1 + np.exp(-z))
        return self.output

    def backward(self, output_grad):
        return output_grad * self.output * (1 - self.output)


class ReLU(Layer):
    def forward(self, z):
        self.input = z
        return np.maximum(0, z)

    def backward(self, output_grad):
        return output_grad * (self.input > 0).astype(float)


class Softmax(Layer):
    def forward(self, z):
        exp_z = np.exp(z - np.max(z, axis=1, keepdims=True))
        self.output = exp_z / np.sum(exp_z, axis=1, keepdims=True)
        return self.output

    def backward(self, output_grad):
        batch_size, num_classes = self.output.shape
        grad_input = np.empty_like(output_grad)
        for i in range(batch_size):
            y = self.output[i].reshape(-1, 1)
            jacobian = np.diagflat(y) - y @ y.T
            grad_input[i] = jacobian @ output_grad[i]
        return grad_input
