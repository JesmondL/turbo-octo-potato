# -*- coding: utf-8 -*-
"""
Author: Jesmond Lee
Date: 12/1/2018
Python 3.5
"""
#sudo install python3-setuptools
#sudo easy_install3 pip
#sudo pip3.5 install --upgrade pip3.5
#sudo pip3.5 install theano
#sudo pip3.5 install --upgrade theano
#sudo pip3.5 install tensorflow
#sudo pip3.5 install --upgrade tensorflow
#sudo pip3.5 install keras
#sudo pip3.5 install --upgrade keras

# DATA PROCESSING------------------------------------
# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Importing the dataset
dataset = pd.read_csv('/home/turbo-octo-potato/Deep_Learning_A_Z/SupervisedDeepLearning/Artificial_Neural_Network_ANN/Churn_Modelling.csv')
X = dataset.iloc[:, 3: 13].values #credit score, geography, gender, age, tenure, balance, numProducts, HasCrCa, Member, Salary
Y = dataset.iloc[:, 13].values #exited (desire to learn this outcome)

# Encoding categorical data
# Encoding the Independent Variable that contains text to enum
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
labelencoder_X_1 = LabelEncoder() #categorize country name to enum
X[:, 1] = labelencoder_X_1.fit_transform(X[:, 1])
labelencoder_X_2 = LabelEncoder() #categorize gender name to enum
X[:, 2] = labelencoder_X_2.fit_transform(X[:, 2])
# insert num of dummy variable columns based on num of categories (applicable if category is more than 2)
# country enum has 3 cats and has no relational order
onehotencoder = OneHotEncoder(categorical_features = [1])
X = onehotencoder.fit_transform(X).toarray()
# 3 colums are inserted but only need 2 due to the combination of 00, 01 and 10
# remove 1 dummy variable column to avoid dummy variable trap
X = X[:, 1:]

# Splitting the dataset into the Training set and Test set
# Categorical data in the dataset must be encoded
from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.2, random_state = 0)

# Feature Scaling
from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

# ANN CREATION---------------------------------------
import keras
from keras.models import Sequential #initialize NN
from keras.layers import Dense #create layers in NN

classifier = Sequential()
# input layer to 1st hidden layer
# 11 indepedent variable as input 
# 6 hidden layer by average of in and out, average =(11+1)/2=6
# rectifier activation method
classifier.add(Dense(output_dim=6, init='uniform', activation='relu', input_dim=11))
# 2nd hidden layer 
classifier.add(Dense(output_dim=6, init='uniform', activation='relu'))
# output layer
# 2 output category, is 1 and sigmoid
# >2 output category, is num of category-1 and softmax
classifier.add(Dense(output_dim=1, init='uniform', activation='sigmoid'))   
# complie with SGD type adam http://ruder.io/optimizing-gradient-descent/index.html#adam
# model use accuracy cutarian to improve the model
classifier.compile(optimizer='adam', loss='binary_crossentropy',
                    metrics=['accuracy'])
# fit ANN to training set
classifier.fit(X_train, Y_train, batch_size=10, nb_epoch=1000)

# MAKE PREDICTION AND EVALUATE MODEL-----------------

# Predicting the Test set results
Y_pred = classifier.predict(X_test)
# Result change to true/false
Y_pred = (Y_pred > 0.5)
# Making the Confusion Matrix
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(Y_test, Y_pred)
# Accuracy
acc = (cm [0,0] + cm [1,1])/(sum(sum(cm)))

# New prediction, convert input to numeric data, apply transformation
#new_prediction = classifier.predict(sc.transform(np.array([[0.0,0,600,1,40,3,60000,2,1,1,50000]])))
#new_prediction = (new_prediction > 0.5)

# EVALUATE, IMPROVE, TUNNING -----------------------
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score
from keras.models import Sequential
from keras.layers import Dense 
def build_classifier():
    classifier = Sequential()
    classifier.add(Dense(units=6, kernel_initializer='uniform', activation='relu', input_dim=11))
    classifier.add(Dense(units=6, kernel_initializer='uniform', activation='relu'))
    classifier.add(Dense(units=1, kernel_initializer='uniform', activation='sigmoid'))   
    classifier.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return classifier
classifier = KerasClassifier(build_fn = build_classifier,batch_size=10, nb_epoch=1000)
# 10 folds = train model 10 times
accuracies = cross_val_score(estimator = classifier, X = X_train, y = Y_train, cv=10, n_jobs=-1)
mean = accuracies.mean()
variance = accuracies.std()