import os
import urllib.request
import gzip
import numpy as np

def download(url, filepath):
    """Downloads a file from a URL if it doesn't exist."""
    if not os.path.exists(filepath):
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, filepath)

def load_images(filepath):
    """Loads MNIST image file."""
    with gzip.open(filepath, 'rb') as f:
        _ = int.from_bytes(f.read(4), 'big')  # magic number
        num_images = int.from_bytes(f.read(4), 'big')
        rows = int.from_bytes(f.read(4), 'big')
        cols = int.from_bytes(f.read(4), 'big')
        images = np.frombuffer(f.read(), dtype=np.uint8)
        images = images.reshape(num_images, rows * cols)
        return images

def load_labels(filepath):
    """Loads MNIST label file."""
    with gzip.open(filepath, 'rb') as f:
        _ = int.from_bytes(f.read(4), 'big')  # magic number
        num_labels = int.from_bytes(f.read(4), 'big')
        labels = np.frombuffer(f.read(), dtype=np.uint8)
        return labels

def one_hot_encode(labels, num_classes=10):
    """One-hot encodes the labels."""
    one_hot = np.zeros((labels.shape[0], num_classes), dtype=np.float32)
    one_hot[np.arange(labels.shape[0]), labels.astype(int)] = 1
    return one_hot

def load_mnist(data_dir="data_files/mnist", normalize=True, flatten=True):
    """Downloads and loads the MNIST dataset."""
    os.makedirs(data_dir, exist_ok=True)

    urls = {
        "train_images": "https://storage.googleapis.com/cvdf-datasets/mnist/train-images-idx3-ubyte.gz",
        "train_labels": "https://storage.googleapis.com/cvdf-datasets/mnist/train-labels-idx1-ubyte.gz",
        "test_images": "https://storage.googleapis.com/cvdf-datasets/mnist/t10k-images-idx3-ubyte.gz",
        "test_labels": "https://storage.googleapis.com/cvdf-datasets/mnist/t10k-labels-idx1-ubyte.gz",
    }
    files = {key: os.path.join(data_dir, url.split('/')[-1]) for key, url in urls.items()}

    # Download if needed
    for key in files:
        download(urls[key], files[key])

    # Load data
    train_images = load_images(files["train_images"])
    train_labels = load_labels(files["train_labels"])
    test_images = load_images(files["test_images"])
    test_labels = load_labels(files["test_labels"])

    if normalize:
        train_images = train_images.astype(np.float32) / 255.0
        test_images = test_images.astype(np.float32) / 255.0

    if not flatten:
        train_images = train_images.reshape(train_images.shape[0], 1, 28, 28)
        test_images = test_images.reshape(test_images.shape[0], 1, 28, 28)

    # 🔥 NEW: One-hot encode the labels
    train_labels = one_hot_encode(train_labels, num_classes=10)
    test_labels = one_hot_encode(test_labels, num_classes=10)

    # Pack datasets
    train_dataset = (train_images, train_labels)
    test_dataset = (test_images, test_labels)

    return train_dataset, test_dataset
