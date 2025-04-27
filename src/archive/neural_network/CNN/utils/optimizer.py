import layers.base as base

class SGD():
    def __init__(self, model, learning_rate=0.01):
        self.model = model
        self.learning_rate = learning_rate

    def step(self):
        for layer in self.model.layers:
            if isinstance(layer, base.TrainableLayer):
                layer.update_parameters(self.learning_rate)
