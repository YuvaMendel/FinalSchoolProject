import numpy as np
from fully_connected import Network  # Import the Network class from your module
from sklearn.datasets import fetch_openml

# Load and preprocess the MNIST dataset
def load_mnist():
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

    return x_train, y_train, x_test, y_test

# Load the MNIST data
x_train, y_train, x_test, y_test = load_mnist()

# Initialize the neural network
network = Network(sizes=[784, 128, 10], activation_function='relu', loss_function='categorical_crossentropy')

# Train the network using stochastic gradient descent
network.stochastic_gradient_descent(x_train, y_train, learning_rate=0.002, batch_size=32, epochs=30)

# Test the network
predictions = network.forward(x_test)
predicted_labels = np.argmax(predictions, axis=1)
actual_labels = np.argmax(y_test, axis=1)

# Calculate accuracy
accuracy = np.mean(predicted_labels == actual_labels)
print(f"Test accuracy: {accuracy * 100:.2f}%")

# Save the trained model
network.save('mnist_model')  # Save the model to a file named 'mnist_model' in the current directory