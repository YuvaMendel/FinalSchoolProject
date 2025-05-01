import numpy as np
class Tester:
    def __init__(self, model, loss_function=None):
        self.model = model
        self.loss_function = loss_function

    def test(self, dataloader):
        loss = 0
        correct = 0
        for inputs, targets in dataloader:
            # Forward pass
            output = self.model.forward(inputs)
            if self.loss_function is not None:
                loss += self.loss_function.forward(output, targets)
            predictions = np.argmax(output, axis=1)
            true_labels = np.argmax(targets, axis=1)
            correct += np.sum(predictions == true_labels)
        if self.loss_function is not None:
            print(f"Test Loss: {loss / len(dataloader)}")
        print(f"Accuracy: {correct / len(dataloader)}")
