import numpy as np

#This file traines a fully connected Neural Network

class Network:
    def __init__(self, sizes):
        """This Function initializes the network.
           sizes is a list that contains the size of each layer
        """
        self.layers = []
        for i in range(1,len(sizes)):
            self.layers.append(Layer(sizes[i], sizes[i-1]))
        
        
class Layer:
    def __init__(self,size, prev_layer_size):
        """This Function initializes a layer.
        this class will be used Only inside network.
        size is the amount of neurons in th layer
        prev_layer_size is the amount of nurons in the previous layer, needed for the weights matrix
        initializes weights matrix with Xavier Initialization Formula
        """
        self.weights = Layer.xavier_initialization(prev_layer_size, size)
        self.biases = np.zeros(size)
        self.last_activation = None
        self.last_gradient = None
    
    @staticmethod
    def xavier_initialization(n_in,n_out):
        """static method that initializes a weights matrix for a layer
           n_in is the amount of neurons layer before
           n_out is the amount of neurons is current layer"""
        limit = np.sqrt(6/(n_in + n_out))
        weights = np.random.uniform(-limit, limit, (n_in, n_out))
        return weights

def sigmoid(n):
    return 1/(1+np.exp(-n))
