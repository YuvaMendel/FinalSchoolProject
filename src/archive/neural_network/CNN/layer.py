from abc import ABC, abstractmethod


class Layer(ABC):
    @abstractmethod
    def forward(self, input_data):
        pass

    @abstractmethod
    def backward(self, output_grad):
        pass