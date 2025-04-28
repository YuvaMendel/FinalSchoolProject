import numpy as np


class DataLoader:
    def __init__(self, dataset, batch_size, shuffle=True):
        self.images, self.labels = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.indices = np.arange(len(self.images), dtype=np.int32)
        self.current_index = 0

    def __iter__(self):
        if self.shuffle:
            np.random.shuffle(self.indices)
        self.current_index = 0
        return self

    def __next__(self):
        if self.current_index >= len(self.images):
            raise StopIteration
        start = self.current_index
        end = min(self.current_index + self.batch_size, len(self.indices))
        batch_indices = self.indices[start:end]
        batch_images_data = self.images[batch_indices]
        batch_labels_data = self.labels[batch_indices]
        self.current_index = end
        return batch_images_data, batch_labels_data
