from ..layers import Layer, TrainableLayer

class SGD:
    def __init__(self, model):
        self.model = model

    def step(self, learning_rate=0.01):
        for layer in self.model.layers:
            if isinstance(layer, TrainableLayer):
                layer.update_parameters(learning_rate)
