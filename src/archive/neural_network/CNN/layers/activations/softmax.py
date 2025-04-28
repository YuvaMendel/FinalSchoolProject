import numpy as np
from layers import Layer


class Softmax(Layer):
    def forward(self, z):
        # z: shape (batch_size, num_classes)
        exps = np.exp(z - np.max(z, axis=1, keepdims=True))  # stability trick
        self.output = exps / np.sum(exps, axis=1, keepdims=True)
        return self.output

    def backward(self, output_grad):
        # Assumes softmax used with cross-entropy loss
        # and that loss.backward() returned (softmax_output - true_labels)
        return output_grad
