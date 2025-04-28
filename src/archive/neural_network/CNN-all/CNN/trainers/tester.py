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
                loss = self.loss_function.forward(output, targets)
                loss += loss
            if max(output) == max(targets):
                correct += 1
        if loss > 0:
            print(f"Test Loss: {loss / len(dataloader)}")
        print(f"Accuracy: {correct / len(dataloader)}")
