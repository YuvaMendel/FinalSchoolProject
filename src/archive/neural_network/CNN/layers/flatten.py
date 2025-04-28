import numpy as np
from layers import Layer


class Flatten(Layer):
    def __init__(self):
        super().__init__()
        self.input_shape = None

    def forward(self, input_data):
        self.input_shape = input_data.shape
        return input_data.reshape(input_data.shape[0], -1)

    def backward(self, output_grad):
        return output_grad.reshape(self.input_shape)

