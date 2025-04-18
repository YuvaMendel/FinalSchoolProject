import pickle
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_openml

# Import your custom Network class

# Load MNIST data
mnist = fetch_openml('mnist_784')

# Prepare the data (normalize pixel values and extract target labels)
X = mnist.data / 255.0  # Normalize to [0, 1]
y = mnist.target.astype(int)  # Convert labels to integers

# Load the neural network from the pickle file
with open('mnist_model', 'rb') as file:  # Replace with your actual file path
    neural_network = pickle.load(file)

# Select a random image from the dataset
random_index = np.random.randint(0, len(X))
image = X.iloc[random_index].to_numpy()
actual_label = y.iloc[random_index]

# Reshape the image to match the input size of your network (784 inputs for MNIST)
image_reshaped = image.reshape(1, 784)  # The network expects a flattened 784-length vector

# Use the neural network to predict the class of the image
predicted_output = neural_network.forward(image_reshaped)
predicted_label = np.argmax(predicted_output)  # The predicted class is the index of the max value

# Display the image and result
image = image.reshape(28, 28)  # Reshape image to 28x28 for display

plt.imshow(image, cmap='gray')
plt.title(f'Predicted: {predicted_label}, Actual: {actual_label}')
plt.show()

# Optionally, print the raw output (network probabilities)
# print(f"Network output (raw probabilities): {predicted_output}")
