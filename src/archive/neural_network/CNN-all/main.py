

from CNN.models import CNN
from CNN.layers.activations import Softmax, ReLU
from CNN.layers import MaxPool2D, Conv2D, Flatten, Dense, Input
from CNN.data import DataLoader
from CNN.data.datasets import load_mnist
from CNN.utils import xavier_initializer, SGD
from CNN.losses import CategoricalCrossEntropy
from CNN.trainers import Trainer, Tester

if __name__ == '__main__':
    model = CNN([
        Input((1, 28, 28)),
        Conv2D(1, 16, (3, 3) , xavier_initializer, stride=1, padding=1),
        ReLU(),
        MaxPool2D((2, 2), stride=2),
        Conv2D(16, 32, (3, 3), xavier_initializer, stride=1, padding=1),
        ReLU(),
        MaxPool2D((2, 2), stride=2),
        Flatten(),
        Dense(64, 32 * 7 * 7, xavier_initializer),
        ReLU(),
        Dense(10, 64, xavier_initializer),
        Softmax()
    ])
    optimizer = SGD(model, learning_rate=0.01)
    loss = CategoricalCrossEntropy()
    train_dataset, test_dataset = load_mnist(flatten=False)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    epochs = 10
    trainer = Trainer(model, optimizer, loss)
    trainer.train(train_loader, epochs)
    tester = Tester(model, loss)
    tester.test(test_loader)