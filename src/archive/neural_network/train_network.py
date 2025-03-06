import numpy as np
from fully_connected import Network  # Import the Network class from your module
from sklearn.datasets import fetch_openml
from PIL import Image, ImageEnhance
import random


# Load and preprocess the MNIST dataset
def load_mnist(augment=False):
    # Load the dataset from a local file or download it
    mnist = fetch_openml('mnist_784', version=1, as_frame=False, parser='liac-arff')
    x, y = mnist["data"], mnist["target"]

    # Normalize the images to be between 0 and 1
    x = x / 255.0

    # One-hot encode the labels
    y = np.eye(10)[y.astype(int)]

    # Split the data into training and test sets
    x_train, x_test = x[:60000], x[60000:]
    y_train, y_test = y[:60000], y[60000:]

    if augment:
        x_train = augment_data(x_train)

    return x_train, y_train, x_test, y_test


# Data augmentation functions
def augment_data(images):
    augmented_images = []
    for img_data in images:
        img = Image.fromarray((img_data * 255).astype(np.uint8)).convert('L')  # Convert to image

        # Randomly apply augmentations
        if random.random() > 0.5:
            img = random_rotate(img)
        if random.random() > 0.5:
            img = random_shift(img)
        if random.random() > 0.5:
            img = random_zoom(img)
        if random.random() > 0.5:
            img = add_noise(img)

        augmented_images.append(np.array(img).flatten() / 255.0)  # Normalize and flatten back to original shape

    return np.array(augmented_images)


# Augmentation functions
def random_rotate(image, max_angle=5):
    """Randomly rotate the image by a given angle."""
    angle = random.uniform(-max_angle, max_angle)
    return image.rotate(angle)


def random_shift(image, max_shift=2):
    """Randomly shift the image horizontally or vertically."""
    width, height = image.size
    shift_x = random.randint(-max_shift, max_shift)
    shift_y = random.randint(-max_shift, max_shift)
    return image.transform(
        (width, height),
        Image.AFFINE,
        (1, 0, shift_x, 0, 1, shift_y),
        resample=Image.BICUBIC  # Use BICUBIC as a fallback for resampling
    )


def random_zoom(image, zoom_range=(0.9, 1.1)):
    """Randomly zoom into the image."""
    width, height = image.size

    # Ensure zoom_factor is within the valid range
    zoom_factor = random.uniform(zoom_range[0], zoom_range[1])

    # Ensure the zoom factor does not make the new size too small
    zoom_factor = max(zoom_factor, 0.5)  # Set a lower limit to avoid too small images

    new_width = int(width * zoom_factor)
    new_height = int(height * zoom_factor)

    # Ensure new dimensions are at least 1x1
    new_width = max(1, new_width)
    new_height = max(1, new_height)

    image_resized = image.resize((new_width, new_height), Image.BICUBIC)  # Use BICUBIC for resizing
    left = (new_width - width) / 2
    top = (new_height - height) / 2
    right = (new_width + width) / 2
    bottom = (new_height + height) / 2

    return image_resized.crop((left, top, right, bottom))



def add_noise(image, noise_factor=0.05):
    """Add random noise to the image."""
    image_array = np.array(image)
    noise = np.random.normal(scale=noise_factor, size=image_array.shape)
    noisy_image = np.clip(image_array + noise * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy_image)


# Load the MNIST data
x_train, y_train, x_test, y_test = load_mnist(augment=True)

# Initialize the neural network
network = Network(sizes=[784, 128, 10], activation_function='relu', loss_function='categorical_crossentropy')

# Train the network using stochastic gradient descent with a lower learning rate
network.stochastic_gradient_descent(x_train, y_train, learning_rate=0.01, batch_size=32, epochs=30)

# Test the network
predictions = network.forward(x_test)
predicted_labels = np.argmax(predictions, axis=1)
actual_labels = np.argmax(y_test, axis=1)

# Calculate accuracy
accuracy = np.mean(predicted_labels == actual_labels)
print(f"Test accuracy: {accuracy * 100:.2f}%")

# Save the trained model
network.save('mnist_model')  # Save the model to a file named 'mnist_model' in the current directory
