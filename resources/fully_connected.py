import numpy as np
from math import sqrt

#This file traines a fully connected Neural Network

class Network:
    def __init__(self, sizes):
        """This Function initializes the network.
           sizes is a list that contains the size of each layer
        """
        pass
        
class Layer:
    def __init__(self,size, prev_layer_size):
        """This Function initializes a layer.
        this class will be used Only inside network.
        size is the amount of nurons in th layer
        prev_layer_size is the amount of nurons in the previous layer, needed for the weights matrix
        initializes weights matrix with Xavier Initialization Formula
        """
        self.weights = xavier_initialization(prev_layer_size, size)
    def xavier_initialization(n_in,n_out):
    """initializes a weights matrix for a layer
       n_in is the amount of neurons layer before
       n_out is the amount of neurons is current layer"""
    limit = sqrt(6/(n_in + n_out))
    weights = np.random.uniform(-1*limit, limit, (n_in, n_out))
    return weights
