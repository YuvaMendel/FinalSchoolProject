from abc import ABC, abstractmethod


class Layer(ABC):
    @abstractmethod
    def forward(self, input_data):
        pass

    @abstractmethod
    def backward(self, output_grad):
        pass


class TrainableLayer(Layer):
    def __init__(self):
        self.weights = None
        self.biases = None
        self.weights_gradient = None
        self.biases_gradient = None

    def update_parameters(self, learning_rate):
        self.weights -= learning_rate * self.weights_gradient

        self.biases -= learning_rate * self.biases_gradient
