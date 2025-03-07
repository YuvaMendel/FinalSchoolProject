import numpy as np
from fully_connected import Network  # Import your custom network class
from sklearn.datasets import fetch_openml
from PIL import Image
import random


# Load and preprocess the MNIST dataset
def load_mnist(augment=False):
    mnist = fetch_openml('mnist_784', version=1, as_frame=False, parser='liac-arff')
    x, y = mnist["data"], mnist["target"].astype(int)

    x = x / 255.0  # Normalize the images
    y = np.eye(10)[y]  # One-hot encode labels

    x_train, x_test = x[:60000], x[60000:]
    y_train, y_test = y[:60000], y[60000:]

    if augment:
        x_train = augment_data(x_train)

    return x_train, y_train, x_test, y_test


# Data augmentation functions
def augment_data(images):
    augmented_images = []
    for img_data in images:
        img = Image.fromarray((img_data.reshape(28, 28) * 255).astype(np.uint8))
        if random.random() > 0.5:
            img = random_rotate(img)
        if random.random() > 0.5:
            img = random_shift(img)
        if random.random() > 0.5:
            img = random_zoom(img)
        if random.random() > 0.5:
            img = add_noise(img)
        augmented_images.append(np.array(img).flatten() / 255.0)
    return np.array(augmented_images)


# Augmentation techniques
def random_rotate(image, max_angle=10):
    return image.rotate(random.uniform(-max_angle, max_angle))


def random_shift(image, max_shift=2):
    width, height = image.size
    shift_x = random.randint(-max_shift, max_shift)
    shift_y = random.randint(-max_shift, max_shift)
    return image.transform((width, height), Image.AFFINE, (1, 0, shift_x, 0, 1, shift_y))


def random_zoom(image, zoom_range=(0.9, 1.1)):
    width, height = image.size
    zoom_factor = random.uniform(zoom_range[0], zoom_range[1])
    new_width = int(width * zoom_factor)
    new_height = int(height * zoom_factor)
    image_resized = image.resize((new_width, new_height), Image.BICUBIC)
    left = (new_width - width) / 2
    top = (new_height - height) / 2
    right = (new_width + width) / 2
    bottom = (new_height + height) / 2
    return image_resized.crop((left, top, right, bottom))


def add_noise(image, noise_factor=0.05):
    image_array = np.array(image)
    noise = np.random.normal(scale=noise_factor, size=image_array.shape)
    noisy_image = np.clip(image_array + noise * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy_image)


# Load MNIST data
x_train, y_train, x_test, y_test = load_mnist(augment=True)

# Initialize the network
network = Network(sizes=[784, 128, 10], activation_function='relu', loss_function='categorical_crossentropy')

# Train the network
network.stochastic_gradient_descent(x_train, y_train, learning_rate=0.003, batch_size=32, epochs=30)

# Evaluate the network
predictions = network.forward(x_test)
predicted_labels = np.argmax(predictions, axis=1)
actual_labels = np.argmax(y_test, axis=1)
accuracy = np.mean(predicted_labels == actual_labels)
print(f"Test accuracy: {accuracy * 100:.2f}%")

# Save the model
network.save('mnist_model')
