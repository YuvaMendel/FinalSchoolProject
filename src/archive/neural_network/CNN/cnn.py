import numpy as np
from abc import ABC, abstractmethod
from layer import Layer


class TrainableLayer(Layer):
    def __init__(self):
        self.weights = None
        self.biases = None
        self.weights_gradient = None
        self.biases_gradient = None

    def update_parameters(self, learning_rate):
        self.weights -= learning_rate * self.weights_gradient

        self.biases -= learning_rate * self.biases_gradient


#  class ConvLayer(Layer):


class DenseLayer(Layer):
    def __init__(self, output_size, input_size, initialization):
        """Initializes a layer with weights and biases.
           - output_size: Number of neurons in this layer.
           - input_size: Number of neurons in the previous layer.
           - The weights matrix is initialized using Xavier initialization.
        """
        self.weights = initialization(input_size, output_size)
        self.biases = np.zeros((1, output_size))
        self.output = None

        self.weights_gradient = None
        self.biases_gradient = None

    def forward(self, input_data):
        """Applies the layer's weights and biases to the input data and activates it.
           - input_data: The input from the previous layer.
           - Saves the activations and returns the result.
        """
        z = np.dot(input_data, self.weights) + self.biases
        self.output = z
        return self.output

    def backward(self, output_grad):
        pass
