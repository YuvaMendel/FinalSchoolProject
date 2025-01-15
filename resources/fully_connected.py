import numpy as np

#This file traines a fully connected Neural Network

class Network:
    def __init__(self, sizes):
        """Initializes the network.
           - sizes: A list that contains the number of neurons in each layer.
        """
        self.layers = []
        for i in range(1,len(sizes)):
            self.layers.append(Layer(sizes[i], sizes[i-1]))
    
    def forward(self, input_data):
        """Passes the data through the network layers.
           - input_data: The input to the neural network.
        """
        for layer in self.layers:
            input_data = layer.forward(input_data)
        return input_data
        
        
        
class Layer:
    def __init__(self,size, prev_layer_size, activation=sigmoid):
        """Initializes a layer with weights and biases.
           - size: Number of neurons in this layer.
           - prev_layer_size: Number of neurons in the previous layer.
           - The weights matrix is initialized using Xavier initialization.
        """
        self.weights = Layer.xavier_initialization(prev_layer_size, size)
        self.biases = np.zeros(size)
        self.last_activation = None
        self.last_gradient = None
        self.activation = activation
        
    def forward(self, input_data):
        """Applies the layer's weights and biases to the input data and activates it.
           - input_data: The input from the previous layer.
           - Saves the activations and returns the result.
        """
        z = np.dot(input_data, self.weights) + self.biases
        self.last_activation = self.activation(z)
        return self.last_activation
    
    @staticmethod
    def xavier_initialization(n_in,n_out):
        """Static method to initialize a weights matrix for a layer using Xavier initialization.
           - n_in: Number of neurons in the previous layer.
           - n_out: Number of neurons in the current layer.
        """
        limit = np.sqrt(6/(n_in + n_out))
        weights = np.random.uniform(-limit, limit, (n_in, n_out))
        return weights

def sigmoid(vector):
    return 1 / (1 + np.exp(-vector))
