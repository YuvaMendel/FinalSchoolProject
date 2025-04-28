from .base import Layer


class Input(Layer):
    def __init__(self, input_shape):
        super().__init__()
        self.input = None
        self.input_shape = input_shape

    def forward(self, input_data):
        self.input = input_data
        return input_data

    def backward(self, output_grad):
        return output_grad
