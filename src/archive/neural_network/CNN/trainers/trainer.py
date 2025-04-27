class Trainer:
    def __init__(self, model, optimizer, loss_function):
        """Initializes the Trainer with a model, optimizer, and loss function.
           - model: The neural network model to be trained.
           - optimizer: The optimizer to be used for training.
           - loss_function: The loss function to be used for training.
        """
        self.model = model
        self.optimizer = optimizer
        self.loss_function = loss_function

    def train(self, dataloader, num_epochs):
        for epoch in range(num_epochs):
            for inputs, targets in dataloader:
                # Forward pass
                outputs = self.model.forward(inputs)
                loss = self.loss_function.forward(outputs, targets)
                # Backward pass
                output_grad = self.loss_function.backward()
                self.model.backward(output_grad)
                self.optimizer.step()
