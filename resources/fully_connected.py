import numpy as np
__author__ = "Yuval Mendel"
#This code traines a fully connected Neural Network

class Network:
    def __init__(self, sizes, activation_function='sigmoid', loss_function='mse_loss'):
        """Initializes the network.
           - sizes: A list that contains the number of neurons in each layer.
        """
        
        self.layers = []
        
        self.loss_function = loss_functions[loss_function][0]
        self.loss_derivative = loss_functions[loss_function][1]
        
        self.activation_function = activation_functions[activation_function][0]
        self.activation_derivative = activation_functions[activation_function][1]
        
        for i in range(1,len(sizes)):
            self.layers.append(Layer(sizes[i], sizes[i-1], activation=self.activation_function))
    
    def forward(self, input_data):
        """Passes the data through the network layers.
           - input_data: The input to the neural network.
        """
        for layer in self.layers:
            input_data = layer.forward(input_data)
        return input_data
        
    def backpropagate(self, input_data, target):
        """Finds the gradient.
           - input_data: The input to the neural network.
           - target: The desired output
        """
        # Forward pass to compute output
        output = self.forward(input_data)
        
        
        output_error = self.loss_derivative(output, target)
        
        
        for i in reversed(range(len(self.layers))):
            layer = self.layers[i]
            activation = layer.last_activation
            
            if i == len(self.layers) - 1:
                delta = output_error * self.activation_derivative(activation)
            else:
                next_layer = self.layers[i + 1]
                delta = np.dot(delta, next_layer.weights.T) * self.activation_derivative(activation)
            
            # Compute gradients for weights and biases
            prev_activation = self.layers[i - 1].last_activation if i > 0 else input_data
            layer.weights_gradient = np.dot(prev_activation.T, delta)
            layer.biases_gradient = np.sum(delta, axis=0, keepdims=True)
    
    def update_parameters(self, learning_rate=0.01):
        """Updates the parameters acording to the gradient
           - learning_rate: the impact of the update (if the gradient is a vector then the learning_rate is a scalar that makes the gradient smaller)
        """
        for layer in self.layers:
            layer.weights -= weights_gradient*learning_rate
            layer.biases_gradient -= biases_gradient*learning_rate
            
        
    
        
        
        
class Layer:
    def __init__(self,size, prev_layer_size, activation):
        """Initializes a layer with weights and biases.
           - size: Number of neurons in this layer.
           - prev_layer_size: Number of neurons in the previous layer.
           - The weights matrix is initialized using Xavier initialization.
        """
        self.weights = Layer.xavier_initialization(prev_layer_size, size)
        self.biases = np.zeros(1,size)
        self.last_activation = None
        
        self.weights_gradient = None
        self.biases_gradient = None
        self.activation_function = activation
        
        
    def forward(self, input_data):
        """Applies the layer's weights and biases to the input data and activates it.
           - input_data: The input from the previous layer.
           - Saves the activations and returns the result.
        """
        z = np.dot(input_data, self.weights) + self.biases
        self.last_activation = self.activation_function(z)
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

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def sigmoid_derivative(z):
    sig = sigmoid(z)
    return sig * (1 - sig)

def mse_loss(predicted, target):
    return np.mean((target - predicted) ** 2)

def mse_loss_derivative(predicted, target):
    return 2 * (predicted - target) / target.size

activation_functions = {
    'sigmoid':(sigmoid, sigmoid_derivative)
}

loss_functions = {
    'mse_loss':(mse_loss, mse_loss_derivative)
}