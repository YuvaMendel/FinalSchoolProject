import numpy as np
import pickle
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

    def save(self, file_path):
        """Saves the model to a file.
           - file_path: The path to the file.
        """
        with open(file_path, 'wb') as file:
            pickle.dump(self, file)
    
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
    
    def update_parameters(self, learning_rate):
        """Updates the parameters acording to the gradient
           - learning_rate: the impact of the update (if the gradient is a vector then the learning_rate is a scalar that makes the gradient smaller)
        """
        for layer in self.layers:
            layer.weights -= layer.weights_gradient*learning_rate
            layer.biases -= layer.biases_gradient*learning_rate
            
    def stochastic_gradient_descent(self, dataset, targets, learning_rate=0.01, batch_size=32, epochs=30):
        """Trains the neural network
           - dataset: the training data
           - targets: the desired outcome for each data unit in the data set
           - learning_rate: the pace the network is allowed to change
           - batch_size: the amount of data units in each batch of data
           - epocs: the amount of times the dataset is used
        """
        for epoc in range(epochs):
            total_accuracy = 0
            total_batches = 0

            #  shuffle data
            permutation = np.random.permutation(len(dataset))
            dataset[:] = dataset[permutation]
            targets[:] = targets[permutation]
            for i in range(0, len(dataset), batch_size):
                dataset_batch = dataset[i:i+batch_size]
                targets_batch = targets[i:i+batch_size]
                self.backpropagate(dataset_batch, targets_batch)
                self.update_parameters(learning_rate)
                
                # Compute accuracy for the current batch
                predictions = self.forward(dataset_batch)
                predicted_labels = np.argmax(predictions, axis=1)
                actual_labels = np.argmax(targets_batch, axis=1)
                accuracy = np.mean(predicted_labels == actual_labels)

                total_accuracy += accuracy
                total_batches += 1
            avg_accuracy = total_accuracy / total_batches
            print(f"Epoch {epoc + 1}/{epochs}. Average accuracy: {avg_accuracy * 100:.2f}%")


                
    
        
        
        
class Layer:
    def __init__(self,size, prev_layer_size, activation):
        """Initializes a layer with weights and biases.
           - size: Number of neurons in this layer.
           - prev_layer_size: Number of neurons in the previous layer.
           - The weights matrix is initialized using Xavier initialization.
        """
        self.weights = Layer.xavier_initialization(prev_layer_size, size)
        self.biases = np.zeros((1,size))
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
    
def relu(z):
    return np.maximum(0, z)

def relu_derivative(z):
    return (z > 0).astype(float)



def categorical_crossentropy(predicted, target):
    
    return -np.sum(target * np.log(predicted + 1e-8)) / target.shape[0]

def categorical_crossentropy_derivative(predicted, target):
    return predicted - target

loss_functions = {
    'mse_loss':(mse_loss, mse_loss_derivative),
    'categorical_crossentropy':(categorical_crossentropy, categorical_crossentropy_derivative)
}

activation_functions = {
    'sigmoid':(sigmoid, sigmoid_derivative),
    'relu':(relu, relu_derivative)
}