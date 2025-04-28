import numpy as np
from layers import TrainableLayer


class DenseLayer(TrainableLayer):
    def __init__(self, output_size, input_size, initialization):
        """Initializes a layer with weights and biases.
           - output_size: Number of neurons in this layer.
           - input_size: Number of neurons in the previous layer.
           - The weights matrix is initialized using Xavier initialization.
        """
        super().__init__()
        self.weights = initialization(input_size, output_size)
        self.biases = np.zeros((1, output_size))
        self.output = None
        self.input_data = None

        self.weights_gradient = None
        self.biases_gradient = None

    def forward(self, input_data):
        """Computes the affine transformation: output = input * W + b.
           - input_data: The input from the previous layer.
           - Saves calculation and returns it.
        """
        self.input_data = input_data
        z = np.dot(input_data, self.weights) + self.biases
        self.output = z
        return self.output

    def backward(self, output_grad):

        # output_grad is the gradient of the loss with respect to the output

        #  Calculate the gradient of the loss with respect to weights
        #  dot product of the input data transposed with the output gradient
        self.weights_gradient = np.dot(self.input_data.T, output_grad)

        #  Calculate the gradient of the loss with respect to bias
        #  sum of the output gradient (batch-wise)
        self.biases_gradient = np.sum(output_grad, axis=0, keepdims=True)

        #  Calculate the gradient of the loss with respect to the input (for the next layer)
        #  the gradient of the loss with respect to the input:
        #  the gradient of the loss with respect to the output dot the gradient of the output with respect to the input
        #  (chain rule)
        #  we have the gradient of the loss with respect to the output (output_grad)
        #  the gradient of the output with respect to the input is just the weights
        #  output = input*W + B
        #  so, it is just the dot product of output_grad and weights.T
        input_grad = np.dot(output_grad, self.weights.T)
        return input_grad
