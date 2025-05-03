import numpy as np
import cv2


def augment_mnist(img):
    """
    Apply random transformations to MNIST-like image.
    Expects img of shape (1, 28, 28) or (28, 28) with float32 in [0,1].
    Returns transformed image with shape (1, 28, 28)
    """
    if img.ndim == 3:
        img = img[0]  # squeeze channel dimension

    # Ensure float32 and range [0, 1]
    img = img.astype(np.float32)
    img = np.clip(img, 0, 1)

    # Convert to 8-bit for OpenCV ops
    img_cv = (img * 255).astype(np.uint8)

    # Random rotation between -15 and +15 degrees
    angle = np.random.uniform(-15, 15)
    M = cv2.getRotationMatrix2D((14, 14), angle, 1.0)
    img_cv = cv2.warpAffine(img_cv, M, (28, 28), borderMode=cv2.BORDER_CONSTANT, borderValue=0)

    # Random erosion or dilation
    if np.random.rand() < 0.5:
        kernel = np.ones((2, 2), np.uint8)
        if np.random.rand() < 0.6:  # make it slightly more likely to dilate
            img_cv = cv2.dilate(img_cv, kernel, iterations=1)
        else:
            img_cv = cv2.erode(img_cv, kernel, iterations=1)

    # Small random translation (shift x/y by -2 to 2 pixels)
    tx = np.random.randint(-2, 3)
    ty = np.random.randint(-2, 3)
    M = np.float32([[1, 0, tx], [0, 1, ty]])
    img_cv = cv2.warpAffine(img_cv, M, (28, 28), borderMode=cv2.BORDER_CONSTANT, borderValue=0)

    # Add small Gaussian noise
    img = img_cv.astype(np.float32) / 255.0
    noise = np.random.normal(0, 0.05, img.shape)
    img = np.clip(img + noise, 0, 1)

    return img[np.newaxis, :, :]  # shape (1, 28, 28)
