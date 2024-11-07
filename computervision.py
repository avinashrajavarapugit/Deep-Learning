# -*- coding: utf-8 -*-
"""ComputerVision.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wsLSXjCbjxxba1TQwhFIut_vqzZsg_Km
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, BatchNormalization, Conv2D, MaxPooling2D, Flatten, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import categorical_crossentropy
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import confusion_matrix

physical_devices = tf.config.experimental.list_physical_devices('GPU')
print('No of GPU availabele : ', len(physical_devices))
tf.config.experimental.set_memory_growth(physical_devices[0], True)

import tensorflow_datasets as tfds

tfds.disable_progress_bar()

train_ds, validation_ds, test_ds = tfds.load(
    "cats_vs_dogs",
    split=["train[:40%]", "train[40%:50%]", "train[50%:60%]"],
    as_supervised = True
  )
print('No of training exaamples : %d '%tf.data.experimental.cardinality(train_ds))
print('No of validation examples : %d'%tf.data.experimental.cardinality(validation_ds))
print('No of test examples : %d'%tf.data.experimental.cardinality(test_ds))

"""Auto encoders. python example
MNIST data
"""

import torch
from torch import nn
import torchvision
import torch.nn.functional as F
import matplotlib.pyplot as plt
import numpy as np
rng = np.random.default_rng(123456)

data = torchvision.datasets.MNIST(root='~/data', download = True)
data = data.data
data = data.float() / 255
data = data.view(-1,1,28,28)
print(data.shape)

class AutoEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Flatten(),
            nn.Linear(28*28, 100),
            nn.ReLU(),
            nn.Linear(100, 10),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(10, 100),
            nn.ReLU(),
            nn.Linear(100, 28*28),
            nn.Sigmoid()
        )

    def encode(self, x):
        return self.encoder(x)

    def decode(self, x):
        x = self.decoder(x)
        return x.view(-1,1,28,28)

    def forward(self, x):
        return self.decode(self.encode(x))

model = AutoEncoder().cuda()
opt = torch.optim.Adam(model.parameters())

for epoch in range(25):
    print(f'Epoch {epoch+1}/25')
    for i in range(0, data.shape[0], 32):
        x = data[i:i+32].cuda()
        x_rec = model(x)
        loss = F.binary_cross_entropy(x_rec, x)

        opt.zero_grad()
        loss.backward()
        opt.step()

    data = data[rng.permutation(len(data))]
    print(f'\tloss: {loss.item():.4f}')

plt.figure(figsize=(5,10))

for i in range(5):
    plt.subplot(5, 2, i*2+1, title=f'Train image')
    plt.imshow(np.squeeze(x[i].cpu()), cmap='gray')
    plt.axis('off')

    plt.subplot(5, 2, i*2+2, title='Reconstruction')
    with torch.no_grad(): plt.imshow(np.squeeze(x_rec[i].cpu()), cmap='gray')
    plt.axis('off')
