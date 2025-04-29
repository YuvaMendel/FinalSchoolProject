
import pickle
from CNN.models import CNN
from CNN.layers.activations import Softmax, ReLU
from CNN.layers import MaxPool2D, Conv2D, Flatten, Dense, Input
from CNN.data import DataLoader
from CNN.data.datasets import load_mnist, load_cifar10
from CNN.utils import xavier_initializer, SGD
from CNN.losses import CategoricalCrossEntropy
from CNN.trainers import Trainer, Tester
from CNN.utils import augment_mnist

if __name__ == '__main__':
    model_mnist = CNN([
        Input((1, 28, 28)),

        Conv2D(1, 32, (3, 3), xavier_initializer, stride=1, padding=1),
        ReLU(),
        MaxPool2D((2, 2), stride=2),

        Conv2D(32, 64, (3, 3), xavier_initializer, stride=1, padding=1),
        ReLU(),
        MaxPool2D((2, 2), stride=2),

        Conv2D(64, 64, (3, 3), xavier_initializer, stride=1, padding=1),
        ReLU(),

        Flatten(),
        Dense(128, 64 * 7 * 7, xavier_initializer),
        ReLU(),
        Dense(10, 128, xavier_initializer),
        Softmax()
    ])

    optimizer = SGD(model_mnist)
    loss = CategoricalCrossEntropy()
    train_dataset, test_dataset = load_mnist(flatten=False)
    images, labels = train_dataset
    train_dataset = (images[:50000], labels[:50000])
    validation_dataset = (images[50000:], labels[50000:])
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, transform=augment_mnist)
    validation_loader = DataLoader(validation_dataset, batch_size=32, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    epochs = 30
    trainer = Trainer(model_mnist, optimizer, loss, learning_rate=0.005, decay_epochs=[10, 20],
                      decay_rate=0.3, validator=Tester(model_mnist, loss)
                      , early_stopping=True, patience=5)
    trainer.train(train_loader, epochs, val_dataloader=validation_loader)
    tester = Tester(model_mnist, loss)
    loss, acc = tester.test(test_loader)
    print(f"Test Loss = {loss:.4f}, Accuracy = {acc:.2%}")
    with open('model.pkl', 'wb') as f:
        pickle.dump(model_mnist, f)
