import numpy as np
import tensorflow as tf
from fully_connected import Network  # Import the Network class from your_module

# Load and preprocess the MNIST dataset using TensorFlow
def load_mnist():
    # TensorFlow provides easy access to MNIST data
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

    # Normalize the images to be between 0 and 1
    x_train = x_train / 255.0
    x_test = x_test / 255.0

    # Flatten images to 1D arrays of size 784 (28x28)
    x_train = x_train.reshape(-1, 784)
    x_test = x_test.reshape(-1, 784)

    # One-hot encode the labels
    y_train = tf.keras.utils.to_categorical(y_train, 10)
    y_test = tf.keras.utils.to_categorical(y_test, 10)

    return x_train, y_train, x_test, y_test

# Load the MNIST data
x_train, y_train, x_test, y_test = load_mnist()

# Initialize the neural network
network = Network(sizes=[784, 128, 10], activation_function='relu', loss_function='categorical_crossentropy')

# Train the network using stochastic gradient descent
network.stochastic_gradient_descent(x_train, y_train, learning_rate=0.001, batch_size=32, epocs=30)


predictions = network.forward(x_test)
predicted_labels = np.argmax(predictions, axis=1)
actual_labels = np.argmax(y_test, axis=1)

# Calculate accuracy
accuracy = np.mean(predicted_labels == actual_labels)
print(f"Test accuracy: {accuracy * 100:.2f}%")