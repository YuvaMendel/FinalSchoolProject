import numpy as np


def im2col(input_data, kernel_size, stride):
    """
    Extracts sliding local blocks (patches) from a padded input tensor and flattens them into rows.

    This operation is used to convert a 4D image tensor into a 2D matrix suitable for efficient
    convolution via matrix multiplication.

    Args:
        input_data (ndarray): Input tensor of shape (N, C, H, W), assumed to be padded already.
        kernel_size (tuple): Tuple of (kh, kw), the kernel height and width.
        stride (int): Stride of the convolution.

    Returns:
        patches (ndarray): A 2D array of shape (N * out_h * out_w, C * kh * kw),
                           where each row is a flattened receptive field from the input.
    """
    N, C, H, W = input_data.shape
    kh, kw = kernel_size

    # Calculate output spatial dimensions
    out_h = (H - kh) // stride + 1
    out_w = (W - kw) // stride + 1

    # Define output shape and strides for as_strided
    shape = (N, C, out_h, out_w, kh, kw)
    s0, s1, s2, s3 = input_data.strides
    strides = (s0, s1, s2 * stride, s3 * stride, s2, s3)

    # Extract and reshape patches
    patches = np.lib.stride_tricks.as_strided(input_data, shape=shape, strides=strides)
    patches = patches.transpose(0, 2, 3, 1, 4, 5)  # → (N, out_h, out_w, C, kh, kw)
    patches = patches.reshape(N * out_h * out_w, C * kh * kw)

    return patches


def col2im(patches, input_shape, kernel_size, stride, padding):
    """
    Reconstructs the original input tensor from the flattened patches.

    Args:
        patches (ndarray): A 2D array of shape (N * out_h * out_w, C * kh * kw),
                           where each row is a flattened receptive field from the input.
        input_shape (tuple): Shape of the original input tensor (N, C, H, W).
        kernel_size (tuple): Tuple of (kh, kw), the kernel height and width.
        stride (int): Stride of the convolution.
        padding (int): Padding added to the input during forward pass.

    Returns:
        reconstructed (ndarray): The reconstructed input tensor of shape (N, C, H, W).
    """
    pass
