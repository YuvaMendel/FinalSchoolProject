import numpy as np
from layers import Layer


class MaxPool2D(Layer):
    def __init__(self, pool_size, stride=None, padding=0):
        """Initializes a MaxPool2D layer.
           - pool_size: Size of the pooling window (height, width).
           - stride: Stride of the pooling operation. If None, it defaults to pool_size.
           - padding: Padding added to the input.
        """
        super().__init__()
        if isinstance(pool_size, int):
            self.ph, self.pw = pool_size, pool_size
        else:
            self.ph, self.pw = pool_size

        if stride is None:
            self.stride = self.ph  # default to pool size
        else:
            self.stride = stride
        self.padding = padding
        self.input_data = None
        self.output = None
        self.output_shape = None
        self.mask = None

    def forward(self, input_data):
        self.input_data = np.pad(input_data,((0, 0), (0, 0), (self.padding, self.padding), (self.padding, self.padding)), mode='constant')
        N, C, H, W = self.input_data.shape
        out_h = (H - self.ph) // self.stride + 1
        out_w = (W - self.pw) // self.stride + 1
        self.output_shape = (N, C, out_h, out_w)
        shape = (N, C, out_h, out_w, self.ph, self.pw)
        s0, s1, s2, s3, s4, s5 = self.input_data.strides
        strides = (s0, s1, s2 * self.stride, s3 * self.stride, s4, s5)
        patches = np.lib.stride_tricks.as_strided(self.input_data, shape=shape, strides=strides)
        self.output = np.max(patches, axis=(4, 5))
        self.mask = (patches == self.output[..., np.newaxis, np.newaxis])
        return self.output

    def backward(self, output_grad):
        N, C, H, W = self.input_data.shape
        out_h = (H - self.ph) // self.stride + 1
        out_w = (W - self.pw) // self.stride + 1
        # Expand output_grad to match the mask's shape
        grad_expanded = output_grad[..., np.newaxis, np.newaxis]  # Shape: (N, C, out_h, out_w, 1, 1)

        # Distribute the gradients only where the mask is True
        grad_masked = self.mask * grad_expanded  # Shape: (N, C, out_h, out_w, ph, pw)
        # in grad masked: for each patch (N, C, out_h, out_w)
        # we have the gradient of the max value in the correct position (ph, pw)
        input_grad = np.zeros_like(self.input_data)

        # Same strides as in forward
        shape = (N, C, out_h, out_w, self.ph, self.pw)
        s0, s1, s2, s3, s4, s5 = input_grad.strides
        strides = (s0, s1, s2 * self.stride, s3 * self.stride, s4, s5)
        input_patches = np.lib.stride_tricks.as_strided(input_grad, shape=shape, strides=strides)

        np.add.at(input_patches, (), grad_masked)
        # Add the gradients to the input gradient
        # input_grad += grad_masked
        if self.padding > 0:
            return input_grad[:, :, self.padding:-self.padding, self.padding:-self.padding]
        return input_grad
