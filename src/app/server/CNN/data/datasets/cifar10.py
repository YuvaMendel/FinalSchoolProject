import os
import urllib.request
import tarfile
import numpy as np
import pickle

def download(url, filepath):
    """Downloads a file if it doesn't exist."""
    if not os.path.exists(filepath):
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, filepath)


def load_batch(filepath):
    """Loads a single batch of CIFAR-10."""
    with open(filepath, 'rb') as f:
        batch = pickle.load(f, encoding='bytes')
        data = batch[b'data']  # shape (10000, 3072)
        labels = batch[b'labels']
        data = data.reshape(-1, 3, 32, 32)  # (batch_size, 3, 32, 32)
        return data, np.array(labels)


def load_cifar10(data_dir="data_files/cifar10", normalize=True):
    """Downloads and loads CIFAR-10 dataset."""
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

    # Load all training batches
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

    # Combine images and labels for DataLoader compatibility
    train_dataset = np.stack([train_images, train_labels], axis=1)
    test_dataset = np.stack([test_images, test_labels], axis=1)

    return train_dataset, test_dataset
