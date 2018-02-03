# -*- coding: utf-8 -*-
"""
Author: Jesmond Lee
Date: 12/1/2018
Python 3.5
The learning the workings of ANN using keras library.

First part is DataPreprocessing() of input data, analyze to extract only the 
revelant data that could affect the desire outcome. Change text based input to 
values by labelencoder. Apply OneHotEncoder if text data has more than 2 
categories, and remove 1 column from the OneHotEncoder to avoid dummy variable
trap. Split data into train and test set, and apply fit_transform to train,
transform (centering, scaling) for test. Standard deviation of 1 and 0 mean,
gives higher accuracy.

Second part is Build_Classifier() using keras library Sequential to build the
input layer, hidden layer and output layer. Activation function, rectifier is
used for the hidden layers, output layer uses sigmod due to only 2 categories.
Dropout of 10% in the hidden layer to prevent overfitting (high variance in 
kcross, acc in train set > test set).

loss https://github.com/keras-team/keras/blob/master/keras/losses.py
"""

import time

# DATA PROCESSING--------------------------------------------------------------
# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import StandardScaler
import keras
from keras.models import Sequential # initialize NN
from keras.layers import Dense # create layers in NN
from keras.layers import Dropout # prevent overfitting
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV

def DataPreprocessing():
    # Importing the dataset
    dataset = pd.read_csv('/home/turbo-octo-potato/Deep_Learning_A_Z/SupervisedDeepLearning/Artificial_Neural_Network_ANN/Churn_Modelling.csv')
    #credit score, geography, gender, age, tenure, balance, numProducts, HasCrCa, Member, Salary    
    X = dataset.iloc[:, 3: 13].values 
    #exited (desire to learn this outcome)
    Y = dataset.iloc[:, 13].values 
    
    # Encoding categorical data, Independent Variable that contains text
    from sklearn.preprocessing import LabelEncoder, OneHotEncoder
    labelencoder_X_1 = LabelEncoder() # categorize country name to enum
    X[:, 1] = labelencoder_X_1.fit_transform(X[:, 1])
    labelencoder_X_2 = LabelEncoder() # categorize gender name to enum
    X[:, 2] = labelencoder_X_2.fit_transform(X[:, 2])
    # insert dummy variable columns (applicable if category is more than 2)
    # country enum has 3 cats (FR,GE,SP) and has no relational order
    onehotencoder = OneHotEncoder(categorical_features = [1]) # country column
    X = onehotencoder.fit_transform(X).toarray()
    # num of cats = num of colums inserted, need 2 columns to express 00,01,10
    # remove 1 dummy variable column to avoid dummy variable trap
    X = X[:, 1:]
    
    # Splitting the dataset into the Training set and Test set, 80:20
    # Categorical data in the dataset must be encoded
    from sklearn.model_selection import train_test_split
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.2, random_state = 0)
    
    # Feature Scaling for train and test set
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    return X_train, X_test, Y_train, Y_test

# ANN CREATION-----------------------------------------------------------------
def ANN():
    data = DataPreprocessing()
    classifier = Sequential()
    # input layer to 1st hidden layer with dropout
    # num of hidden layer just use average of in and out as a start
    classifier.add(Dense(units=6, kernel_initializer='uniform', activation='relu', input_dim=11))
    classifier.add(Dropout(rate = 0.1))
    # 2nd hidden layer with dropout
    classifier.add(Dense(units=6, kernel_initializer='uniform', activation='relu'))
    classifier.add(Dropout(rate = 0.1))
    # output layer
    # 2 output category uses sigmoid, otherwise num of category-1 and softmax
    classifier.add(Dense(units=1, kernel_initializer='uniform', activation='sigmoid'))   
    # complie with SGD type adam 
    # model use accuracy cutarian to improve the model
    classifier.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    # fit X_train, Y_train to training set
    classifier.fit(data[0], data[2], batch_size=10, epochs=1)
    
# MAKE PREDICTION AND EVALUATE MODEL-------------------------------------------
    # Predicting the Test set results
    Y_pred = classifier.predict(data[1])
    # Result change to true/false
    Y_pred = (Y_pred > 0.5)
    # Making the Confusion Matrix
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(data[3], Y_pred)
    # Accuracy
    acc = (cm [0,0] + cm [1,1])/(sum(sum(cm)))
    return acc
    
def Predict_this():
# New prediction, convert input to numeric data, apply transformation
    sc = StandardScaler()
    new_prediction = classifier.predict(sc.transform(np.array([[0.0,0,600,1,40,3,60000,2,1,1,50000]])))
    new_prediction = (new_prediction > 0.5)

# EVALUATE, IMPROVE, TUNNING --------------------------------------------------
# Kcross validation 10 folds = train model 10 times
#def Build_Classifier():
#    classifier = Sequential()
#    classifier.add(Dense(units=6, kernel_initializer='uniform', activation='relu', input_dim=11))
#    classifier.add(Dense(units=6, kernel_initializer='uniform', activation='relu'))
#    classifier.add(Dense(units=1, kernel_initializer='uniform', activation='sigmoid'))   
#    classifier.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
#    return classifier
#data = DataPreprocessing()
#classifier = KerasClassifier(build_fn = Build_Classifier,batch_size=10, epochs=100)
#accuracies = cross_val_score(estimator = classifier, X = data[0], y = data[2], cv=10, n_jobs=-1)
#mean = accuracies.mean()
#variance = accuracies.std()

# GridSearchCV
def Build_Classifier(optimizer, loss):
    classifier = Sequential()
    classifier.add(Dense(units=6, kernel_initializer='uniform', activation='relu', input_dim=11))
    classifier.add(Dropout(rate = 0.05))
    classifier.add(Dense(units=6, kernel_initializer='uniform', activation='relu'))
    classifier.add(Dropout(rate = 0.05))
    classifier.add(Dense(units=1, kernel_initializer='uniform', activation='sigmoid'))   
    classifier.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])
    return classifier
start_time = time.time()
data = DataPreprocessing()
classifier = KerasClassifier(build_fn = Build_Classifier)
# Dictionary of hyper parameters
parameters = {'batch_size':[96, 96, 96, 96, 96, 96], 
'epochs':[1,1,1,1,1,1], 
'optimizer':['adam','nadam','sgd','rmsprop','adagrad','adamax'],
'loss':['binary_crossentropy','mean_squared_error','kullback_leibler_divergence','hinge','mean_squared_logarithmic_error','poisson']}
grid_search = GridSearchCV(estimator = classifier, param_grid = parameters, scoring = 'accuracy', 
                           cv = 2)
grid_search = grid_search.fit(data[0], data[2])
best_parameter = grid_search.best_params_
best_accuracy = grid_search.best_score_
print("%s seconds" %(time.time() - start_time))
#11-6-6-1 no dropout, loss=binary_crossentropy, batch_size 25, epochs 500, adam, 84.6375%
#11-6-6-1 0.15dropout, loss=poisson, batch_size 192, epochs 50, adam, 80.4% 773.7297103404999 seconds
