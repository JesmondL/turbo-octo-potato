# -*- coding: utf-8 -*-
"""
Author: Jesmond Lee
Date: 22/1/2018
Python 3.5

CNN is used for computer vision.

First part is the structure of how the images will be processed to identify key
feature and convert these information into neurons for feeding into a ANN for prediction.
Input image - color pixles are converted to values for application of feature dectectors.
Images will be forced to dimension 64x64, as input size could be different, a consistent
input attribute is necessary for accuracy.
Feature detector/ Kerner/ Filter - feature detectors (num is ^2) of a square shape. 
1 feature detector ties to 1 feature map (a reduced size of processed image details). End 
of each detection will move to the next area of pixles by the stride.                                                                         
Feature map/ convolt feature/ activation map - feature map resp for detection different 
features (Relu activation)
Max pooling - further reduce the size of feature map before passing to the network. 
Spacial characteristic of feature map is kept intact. 2x2 would half the feature map size.
Flatterning - maps are converted to a vector of input for network to process

Second part is the obtaining the train and test date to begin processing of images.
Full connection - network to process the inputs with layers to give an predict output
"""

from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.layers import Dropout
from keras.models import load_model
import numpy as np
from keras.preprocessing import image
from keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, TensorBoard

# INITIALIZE CNN --------------------------------------------------------------
def create_CNN():
    classifier = Sequential()
    # 64 feature detectors of 3x3, image channels color RGB(3), 128x128 dimension.
    # tf backend is written in dim, dim, channels, Theano backend is channel, dim, dim
    classifier.add(Conv2D(32, (3, 3), input_shape=(64, 64, 3), activation = 'relu'))
    # reduce feature map size by 2. Reduce complexity not performance
    classifier.add(MaxPooling2D(pool_size=(2,2)))
    # 2nd convolution layer to improve the accuracy, common to x2 feature dectectors
    classifier.add(Conv2D(32, (3, 3), activation = 'relu'))
    classifier.add(MaxPooling2D(pool_size=(2,2)))
    # 3rd convolution layer
    classifier.add(Conv2D(64, (3, 3), activation = 'relu'))
    classifier.add(MaxPooling2D(pool_size=(2,2)))
    # flatten to a vector of input
    classifier.add(Flatten())
    # full connection
    classifier.add(Dense(units=64, activation='relu'))
    classifier.add(Dropout(0.3))
    classifier.add(Dense(units=1, activation='sigmoid'))
    # complie CNN
    classifier.compile(optimizer='adam',loss='binary_crossentropy', metrics=['accuracy'])
    return classifier

# TRAINING CNN ----------------------------------------------------------------
def train_CNN(classifier):
    es = EarlyStopping(monitor='val_loss', min_delta=1e-10, patience=10, verbose=1)
    rlr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, verbose=1)
    mcp = ModelCheckpoint(filepath='weights.h5', monitor='val_loss', verbose=1, save_best_only=True, save_weights_only=True)
    tb = TensorBoard('logs')
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
            target_size=(64, 64),# align with convolution input shape
            batch_size=96,
            class_mode='binary')# 2 class mode 
    
    test_set = test_datagen.flow_from_directory(
            'dataset/test_set',
            target_size=(64, 64),# align with convolution input shape
            batch_size=96,
            class_mode='binary') # 2 class mode 
    
    classifier.fit_generator(
            training_set,
            steps_per_epoch=8000/96,# num of training images, total/batch size
            epochs=100, # num of iteration on the data
            verbose=2,
            callbacks=[es, rlr,mcp, tb],
            validation_data=test_set,
            validation_steps=2000/96,# num of test images, total/batch size
            workers = 10, # maximum num of processor to use
            max_queue_size = 100, # size of generator queue
            use_multiprocessing = True, # enable multiprocessing
            shuffle=True) # shuffle the training data
    
    # Save model
    classifier.save('model.h5')
     
    # Save loss history to file
    myFile = open('history.txt', 'w+')
    myFile.write(classifier.history)
    myFile.close()
        
# SINGLE PREDICTION -----------------------------------------------------------
def predict_CNN():
    classifier = load_model('/model.h5')
    test_image = image.load_img('dataset/single_prediction/cat_or_dog_1.jpg', 
                                target_size=(64,64))
    test_image = image.img_to_array(test_image)
    test_image = np.expand_dims(test_image, axis=0)
    result = classifier.predict(test_image)
    #training_set.class_indices
    if result [0][0] == 1:
        prediction = 'cat'
    else:
        prediction = 'dog'
        
CNN = create_CNN()
train_CNN(CNN)