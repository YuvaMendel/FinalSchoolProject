import os
import urllib.request
import tarfile
import numpy as np
import pickle

def download(url, filepath):
    """Downloads a file from a URL if it doesn't exist."""
    if not os.path.exists(filepath):
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, filepath)

def load_batch(filepath):
    """Loads a single CIFAR-10 batch."""
    with open(filepath, 'rb') as f:
        batch = pickle.load(f, encoding='bytes')
        data = batch[b'data']  # shape (10000, 3072)
        labels = batch[b'labels']
        data = data.reshape(-1, 3, 32, 32)  # (batch_size, 3, 32, 32)
        return data, np.array(labels)

def one_hot_encode(labels, num_classes=10):
    """One-hot encodes the labels."""
    one_hot = np.zeros((labels.shape[0], num_classes), dtype=np.float32)
    one_hot[np.arange(labels.shape[0]), labels.astype(int)] = 1
    return one_hot

def load_cifar10(data_dir="data_files/cifar10", normalize=True, one_hot=True):
    """Downloads and loads the CIFAR-10 dataset."""
    os.makedirs(data_dir, exist_ok=True)

    url = "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"
    archive_path = os.path.join(data_dir, "cifar-10-python.tar.gz")
    extracted_folder = os.path.join(data_dir, "cifar-10-batches-py")

    # Download and extract if needed
    if not os.path.exists(extracted_folder):
        download(url, archive_path)
        print(f"Extracting {archive_path}...")
        with tarfile.open(archive_path, 'r:gz') as tar:
            tar.extractall(path=data_dir)

    # Load training batches
    train_data = []
    train_labels = []
    for i in range(1, 6):
        batch_path = os.path.join(extracted_folder, f"data_batch_{i}")
        data, labels = load_batch(batch_path)
        train_data.append(data)
        train_labels.append(labels)
    train_images = np.concatenate(train_data, axis=0)
    train_labels = np.concatenate(train_labels, axis=0)

    # Load test batch
    test_batch_path = os.path.join(extracted_folder, "test_batch")
    test_images, test_labels = load_batch(test_batch_path)

    if normalize:
        train_images = train_images.astype(np.float32) / 255.0
        test_images = test_images.astype(np.float32) / 255.0

    if one_hot:
        train_labels = one_hot_encode(train_labels, num_classes=10)
        test_labels = one_hot_encode(test_labels, num_classes=10)

    # Pack datasets
    train_dataset = (train_images, train_labels)
    test_dataset = (test_images, test_labels)

    return train_dataset, test_dataset
