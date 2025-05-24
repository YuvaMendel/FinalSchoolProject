import numpy as np
from multiprocessing.pool import ThreadPool


class DataLoader:
    def __init__(self, dataset, batch_size, shuffle=True, transform=None):
        self.images, self.labels = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.indices = np.arange(len(self.images), dtype=np.int32)
        self.current_index = 0
        self.transform = transform
        self.pool = ThreadPool(processes=4) if transform else None

    def __iter__(self):
        if self.shuffle:
            np.random.shuffle(self.indices)
        self.current_index = 0
        return self

    def __next__(self):
        """Return the next batch of images and labels."""
        if self.current_index >= len(self.images):
            raise StopIteration
        start = self.current_index
        end = min(self.current_index + self.batch_size, len(self.indices))
        batch_indices = self.indices[start:end]
        batch_images_data = self.images[batch_indices]
        batch_labels_data = self.labels[batch_indices]
        if self.transform:
            batch_images_data = np.stack(self.pool.map(self.transform, batch_images_data))
        self.current_index = end
        return batch_images_data, batch_labels_data

    def __len__(self):
        return len(self.images)

    def __del__(self):
        if self.pool is not None:
            self.pool.close()
            self.pool.join()
