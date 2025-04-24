import numpy as np


def im2col(input_data, kernel_size, stride):  # I am too cool
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


def col2im(patch_grads, input_shape, kernel_size, stride, padding):
    """
    Reconstructs the full input gradient tensor from local patch gradients (reverse of im2col).

    This function takes the per-output-location patch gradients (e.g., from backpropagation)
    and scatters them back into the full input tensor, summing overlapping contributions.

    Args:
        patch_grads (ndarray): Gradient patches of shape (N, C, kh, kw, out_h, out_w),
                               where each patch is a (C × kh × kw) gradient for an output pixel.
        input_shape (tuple): Shape of the padded input tensor, e.g. (N, C, H, W).
        kernel_size (tuple): Tuple (kh, kw), height and width of the kernel.
        stride (int): Stride used during the forward convolution.
        padding (int): Padding used during the forward convolution.

    Returns:
        input_grad (ndarray): Reconstructed input gradient tensor of shape:
                              (N, C, H - 2 * padding, W - 2 * padding) if padding > 0,
                              or (N, C, H, W) if no padding.
    """
    N, C, H, W = input_shape
    kh, kw = kernel_size
    out_h = patch_grads.shape[4]
    out_w = patch_grads.shape[5]
    input_grad_padded = np.zeros(input_shape, dtype=patch_grads.dtype)
    # Calculate the strided view shape and strides
    shape = (N, C, out_h, out_w, kh, kw)
    s0, s1, s2, s3 = input_grad_padded.strides
    strides = (s0, s1, s2 * stride, s3 * stride, s2, s3)

    # Create a writeable strided view into input_grad_padded
    patch_view = np.lib.stride_tricks.as_strided(
        input_grad_padded,
        shape=shape,
        strides=strides,
        writeable=True
    )

    # Transpose patches to match patch_view shape
    patch_reshaped = patch_grads.transpose(0, 1, 4, 5, 2, 3)
    np.add.at(patch_view, (...,), patch_reshaped)
    if padding > 0:
        return input_grad_padded[:, :, padding:-padding, padding:-padding]
    return input_grad_padded


