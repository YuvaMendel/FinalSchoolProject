import numpy as np
from layers import TrainableLayer
from utils import im2col, col2im


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

        #  The biases have the shape (out_channels) (one bias per filter)
        self.biases = np.zeros(out_channels)

        #  The Weights have the shape (out_channels, in_channels, kh, kw)
        #  for each filter, we have (in_channels * kh * kw) weights (the shape of the kernel)
        self.weights = initialization(out_channels, in_channels, kh, kw)

        self.weights_gradient = np.zeros_like(self.weights)
        self.biases_gradient = np.zeros_like(self.biases)

        self.in_channels = in_channels
        self.out_channels = out_channels

        self.stride = stride
        self.kh = kh
        self.kw = kw

        self.padding = padding

        self.input_data = None
        self.output = None
        self.output_shape = None
        self.patches = None

    def forward(self, input_data):
        """Computes the convolution operation.
           - input_data: The input from the previous layer.
           - Saves calculation and returns it.
        """
        self.input_data = np.pad(input_data, ((0,0), (0,0), (self.padding, self.padding), (self.padding, self.padding)), mode='constant')
        weights_for_multiplication = self.weights.reshape(self.out_channels, -1).T

        self.patches = im2col(self.input_data, (self.kh, self.kw), self.stride)
        self.output = np.dot(self.patches, weights_for_multiplication) + self.biases
        N, _, H, W = self.input_data.shape
        out_h = (H - self.kh) // self.stride + 1
        out_w = (W - self.kw) // self.stride + 1
        self.output_shape = (N, self.out_channels, out_h, out_w)
        self.output = self.output.reshape(N, out_h, out_w, self.out_channels).transpose(0, 3, 1, 2)
        return self.output

    def backward(self, output_grad):
        """Computes the gradient of the loss with respect to the input (and with respect to the weights and biases).
           - output_grad: The gradient of the loss with respect to the output.
           - Returns the gradient of the loss with respect to the input.
        """

        #  reshape the output gradient to match the shape of the patches
        output_grad_flat = output_grad.transpose(0, 2, 3, 1).reshape(-1, self.out_channels)
        #  Calculate the gradient of the loss with respect to weights
        self.weights_gradient = np.dot(output_grad_flat.T, self.patches)
        self.weights_gradient = self.weights_gradient.reshape(self.out_channels, self.in_channels, self.kh, self.kw)

        #  Calculate the gradient of the loss with respect to bias
        #  sum of the output gradient (batch-wise)
        self.biases_gradient = np.sum(output_grad_flat, axis=0)

        #  Calculate the gradient of the loss with respect to the input (for the next layer)
        # ----------------------------------------------------------
        # Gradient w.r.t. the input (∂L/∂input) - Intuition:
        #
        # For each input pixel:
        #   - Look at all output pixels that were computed using it.
        #   - Each of those output pixels has a gradient telling how much it wants to change.
        #   - The input pixel affected that output pixel through a specific weight in the filter.
        #   - So we multiply the output gradient by that weight (the strength of the connection).
        #   - Then we sum up all of these contributions.
        #
        # From the output's perspective:
        #   - Each output pixel "spreads" its gradient back to the input patch it came from.
        #   - It does so proportionally to the filter weights used during the forward pass.
        #
        # The final result tells each input pixel: "Here's how much you need to change to reduce the loss."
        # ----------------------------------------------------------
        N, C, H, W = self.input_data.shape
        out_h = (H - self.kh) // self.stride + 1
        out_w = (W - self.kw) // self.stride + 1
        input_grad_patches = np.dot(output_grad_flat, self.weights.reshape(self.out_channels, -1))
        input_grad_patches = input_grad_patches.reshape(N, out_h, out_w, C, self.kh, self.kw)
        input_grad_patches = input_grad_patches.transpose(0, 3, 4, 5, 1, 2)
        # input_grad_patches holds the gradient of the loss with respect to each input patch.
        # Shape: (N, C, kh, kw, out_h, out_w)
        #
        # For each image in the batch (N), each input channel (C), and each output location (out_h, out_w),
        # this array tells us how much each pixel in the receptive field (defined by the kernel window kh x kw)
        # should change to reduce the loss.
        #
        # This will be scattered back into the full input gradient image, summing overlapping contributions.
        # ----------------------------------------------------------
        input_grad = col2im(input_grad_patches, self.input_data.shape, (self.kh, self.kw), self.stride, self.padding)
        return input_grad



