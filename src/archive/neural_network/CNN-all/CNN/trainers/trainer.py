from time import time
import copy
import numpy as np


class Trainer:
    def __init__(self, model, optimizer, loss_function,
                 learning_rate=0.01, decay_epochs=None,
                 decay_rate=None, validator=None,
                 early_stopping=False, patience=5):
        """Initializes the Trainer with a model, optimizer, and loss function.
           - model: The neural network model to be trained.
           - optimizer: The optimizer to be used for training.
           - loss_function: The loss function to be used for training.
        """
        self.model = model
        self.best_model_state = None
        self.optimizer = optimizer
        self.loss_function = loss_function
        self.learning_rate = learning_rate
        self.decay_epochs = decay_epochs or []
        self.decay_rate = decay_rate or 0.1
        self.validator = validator
        self.early_stopping = early_stopping
        self.patience = patience

    def train(self, dataloader, num_epochs, val_dataloader=None):
        best_val_acc = -np.Inf
        epochs_no_improve = 0
        for epoch in range(num_epochs):
            total_loss = 0
            t1 = time()
            if epoch in self.decay_epochs:
                self.learning_rate *= self.decay_rate
                print(f"Learning Rate Decayed to {self.learning_rate}")
            print(f"Epoch {epoch + 1}/{num_epochs}", end=", ")

            for inputs, targets in dataloader:
                # Forward pass
                outputs = self.model.forward(inputs)
                loss = self.loss_function.forward(outputs, targets)
                # Backward pass
                output_grad = self.loss_function.backward()
                self.model.backward(output_grad)
                self.optimizer.step(self.learning_rate)
                total_loss += loss
            if len(dataloader) > 0:
                print(f"Loss: {(total_loss/len(dataloader)):.4f}")
            if val_dataloader is not None and self.validator is not None:
                val_loss, val_acc = self.validator.test(val_dataloader)
                print(f"Validation Loss = {val_loss:.4f}, Accuracy = {val_acc:.2%}")
                if self.early_stopping:
                    if val_acc > best_val_acc:
                        best_val_acc = val_acc
                        self.best_model_state = copy.deepcopy(self.model)
                        epochs_no_improve = 0
                    else:
                        epochs_no_improve += 1
                        print(f" (no improvement for {epochs_no_improve} epoch(s))")

                    if epochs_no_improve >= self.patience:
                        print("Early stopping triggered!")
                        self.model = self.best_model_state
                        break
            t2 = time()
            print(f"Time taken: {t2 - t1:.2f} seconds")
