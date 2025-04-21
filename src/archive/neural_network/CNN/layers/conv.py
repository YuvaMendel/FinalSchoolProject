import numpy as np
from base import TrainableLayer


class Conv2D(TrainableLayer):
    def __init__(self, in_channels, out_channels, kernel_size, initialization, stride=1, padding=0):
        """Initializes a Conv2D layer with weights and biases.
           - in_channels: Number of input channels.
           - out_channels: Number of output channels (filters).
           - kernel_size: Size of the convolutional kernel (height, width).
           - initialization: Function to initialize weights.
           - stride: Stride of the convolution.
           - padding: Padding added to the input.
        """
        super().__init__()
        kh, kw = kernel_size

        #  The biases have the shape (1, out_channels) (one bias per filter)
        self.biases = np.zeros((1, out_channels))

        #  The Weights have the shape (out_channels, in_channels, kh, kw)
        #  for each filter, we have (in_channels * kh * kw) weights (the shape of the kernel)
        self.weights = initialization(out_channels, in_channels, kh, kw)

        self.weights_gradient = np.zeros_like(self.weights)
        self.biases_gradient = np.zeros_like(self.biases)

        self.in_channels = in_channels
        self.out_channels = out_channels

        self.stride = stride
        self.kernel_size = (kh, kw)

        self.padding = padding

        self.input_data = None
        self.output = None
        self.output_shape = None

    def forward(self, input_data):
        """Computes the convolution operation.
           - input_data: The input from the previous layer.
           - Saves calculation and returns it.
        """
        self.input_data = np.pad(input_data, ((0,0), (0,0), (self.padding, self.padding), (self.padding, self.padding)), mode='constant')
        pass

    def backward(self, output_grad):
        """Computes the gradient of the loss with respect to the input.
           - output_grad: The gradient of the loss with respect to the output.
           - Returns the gradient of the loss with respect to the input.
        """
        pass

    def _im2col(self): # I am too cool
        N, C, H, W = self.input_data.shape()
        out_h = (H - self.kernel_size[0])//self.stride + 1
        out_w = (W - self.kernel_size[1])//self.stride + 1
        #REMINDER TO USE  np.lib.stride_tricks.as_strided


