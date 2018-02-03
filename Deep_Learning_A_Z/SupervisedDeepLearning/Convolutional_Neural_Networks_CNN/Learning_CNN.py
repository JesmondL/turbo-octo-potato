# -*- coding: utf-8 -*-
"""
Author: Jesmond Lee
Date: 22/1/2018
Python 3.5

Input image - color pixles are converted to values for application of feature dectectors.
Images will be forced to dimension 128x128, as input size could be different, a consistent
input attribute is necessary for accuracy.

Feature detector/ Kerner/ Filter - feature detectors (num is ^2) of a square shape. 
1 feature detector ties to 1 feature map (a reduced size of processed image details). End 
of each detection will move to the next area of pixles by the stride.          
                                                                
Feature map/ convolt feature/ activation map - feature map resp for detection different 
features (Relu activation)

Max pooling - further reduce the size of feature map before passing to the network. 
Spacial characteristic of feature map is kept intact. 2x2 would half the feature map size.

Flatterning - maps are converted to a vector of input for network to process

Full connection - network to process the inputs with layers to give an predict output
"""

from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense

# INITIALIZE CNN --------------------------------------------------------------
classifier = Sequential()
# 64 feature detectors of 3x3, image channels color RGB(3), 128x128 dimension.
# tf backend is written in dim, dim, channels, Theano backend is channel, dim, dim
classifier.add(Conv2D(64, (3, 3), input_shape=(128, 128, 3), activation = 'relu'))
# reduce feature map size by 2. Reduce complexity not performance
classifier.add(MaxPooling2D(pool_size=(2,2)))
# nested convolution layer to improve the accuracy, common to x2 feature dectectors
classifier.add(Conv2D(64, (3, 3), activation = 'relu'))
classifier.add(MaxPooling2D(pool_size=(2,2)))
# flatten to a vector of input
classifier.add(Flatten())
# full connection
classifier.add(Dense(output_dim=64, activation='relu'))
classifier.add(Dense(output_dim=1, activation='sigmoid'))
# complie CNN
classifier.compile(optimizer='adam',loss='binary_crossentropy', metrics=['accuracy'])

#https://keras.io/preprocessing/image/
from keras.preprocessing.image import ImageDataGenerator
train_datagen = ImageDataGenerator(
        rescale=1./255, # rescale pixel value between 0 and 1
        shear_range=0.2,# apply random transaction
        zoom_range=0.2, # how much want to apply random transaction
        horizontal_flip=True)

test_datagen = ImageDataGenerator(rescale=1./255)

training_set = train_datagen.flow_from_directory(
        'dataset/training_set',
        target_size=(128, 128),# align with convolution input shape
        batch_size=96,
        class_mode='binary')# 2 class mode 

test_set = test_datagen.flow_from_directory(
        'dataset/test_set',
        target_size=(128, 128),# align with convolution input shape
        batch_size=96,
        class_mode='binary') # 2 class mode 

classifier.fit_generator(
        training_set,
        steps_per_epoch=80,# num of training images
        epochs=1,
        validation_data=test_set,
        validation_steps=20)# num of test images