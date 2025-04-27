from layers import base


class CNN:
    def __init__(self, layers):
        """Initializes the CNN model with a list of layers.
           - layers: List of layers to be added to the model.
        """
        self.layers = layers

    def forward(self, input_data):
        """Performs a forward pass through the model.
           - input_data: Input data to the model.
           Returns the output of the last layer.
        """
        for layer in self.layers:
            input_data = layer.forward(input_data)
        return input_data

    def backward(self, output_grad):
        """Performs a backward pass through the model.
           - output_grad: Gradient of the loss with respect to the output.
           Returns the gradient of the loss with respect to the input.
        """
        for layer in reversed(self.layers):
            output_grad = layer.backward(output_grad)
        return output_grad

    def update_parameters(self, learning_rate):
        """Updates the parameters of the model using the gradients.
           - learning_rate: Learning rate for the update.
        """
        for layer in self.layers:
            if isinstance(layer, base.TrainableLayer):
                layer.update_parameters(learning_rate)
