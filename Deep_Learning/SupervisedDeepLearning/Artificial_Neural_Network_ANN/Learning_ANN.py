# -*- coding: utf-8 -*-
"""
Author: Jesmond Lee
Date: 12/1/2018
Python 3.5

ANN is used for regression and classification.

First part is DataPreprocessing() of input data, analyze to extract only the 
revelant data column (category) from the csv file that could affect the desire 
outcome. Change any text based data to values by labelencoder. Apply OneHotEncoder
if text data has more than 2 meaning (eg, Yes, No, Maybe), and remove 1 column 
from the OneHotEncoder to avoid dummy variable trap. Split data into train and 
test set, and center the data to have a standard deviation of 1 and 0 mean by
subtract the mean and then divide the result by the standard deviation. Apply 
fit_transform to training data, would obtain the mean and standard deviation 
which is immediately use to tranform the training data. Test data only needs
transform, since the mean and SD was obtained previously from training data.
Resulted data would have better accuracy in the ANN.

Second part is Build_Classifier() using keras library Sequential to build the
input layer, hidden layer and output layer. Activation function, rectifier is
used for the hidden layers, output layer uses sigmod due to only 2 categories.
Dropouts in the hidden layer to prevent overfitting (high variance in 
kcross, acc in train set > test set).

loss https://github.com/keras-team/keras/blob/master/keras/losses.py
"""
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
from keras.models import load_model
from keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, TensorBoard
import time

# DATA PROCESSING--------------------------------------------------------------
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

# INITIALIZE ANN --------------------------------------------------------------
def create_ANN(ipts, u1, u2, u3):
    classifier = Sequential()
    # input layer to 1st hidden layer with dropout
    # num of hidden layer just use average of in and out as a start
    classifier.add(Dense(units=u1, kernel_initializer='uniform', activation='relu', input_dim=ipts))
    classifier.add(Dropout(rate = 0.05))
    # 2nd hidden layer with dropout
    classifier.add(Dense(units=u2, kernel_initializer='uniform', activation='relu'))
    # output layer
    # 2 output category uses sigmoid, otherwise num of category-1 and softmax
    classifier.add(Dense(units=u3, kernel_initializer='uniform', activation='sigmoid'))   
    # complie with SGD type adam 
    # model use accuracy cutarian to improve the model
    classifier.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return classifier
    
# TRAINING ANN ----------------------------------------------------------------
def train_CNN(classifier):  
    es = EarlyStopping(monitor='val_loss', min_delta=1e-10, patience=10, verbose=1)
    rlr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, verbose=1)
    mcp = ModelCheckpoint(filepath='weights.h5', monitor='val_loss', verbose=1, save_best_only=True, save_weights_only=True)
    tb = TensorBoard('logs')
    data = DataPreprocessing()
    # fit X_train, Y_train to training set
    classifier.fit(data[0], data[2], batch_size=192, epochs=100,
                   verbose=2, callbacks=[es, rlr,mcp, tb], shuffle=True)
    
    # Predicting the Test set results
    Y_pred = classifier.predict(data[1])
    # Result change to true/false
    Y_pred = (Y_pred > 0.5)
    # Making the Confusion Matrix
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(data[3], Y_pred)
    # Accuracy
    acc = (cm [0,0] + cm [1,1])/(sum(sum(cm)))
    
    # Save model
    classifier.save('/home/turbo-octo-potato/Deep_Learning_A_Z/SupervisedDeepLearning/Artificial_Neural_Network_ANN/model.h5')
    
    # Save loss history to file
    myFile = open('history.txt', 'w+')
    myFile.write(classifier.history)
    myFile.write(acc)
    myFile.close()

# SINGLE PREDICTION -----------------------------------------------------------
def predict_ANN():
# New prediction, convert input to numeric data, apply transformation
    classifier = load_model('/home/turbo-octo-potato/Deep_Learning_A_Z/SupervisedDeepLearning/Artificial_Neural_Network_ANN/model.h5')
    sc = StandardScaler()
    new_prediction = classifier.predict(sc.transform(np.array([[0.0,0,600,1,40,3,60000,2,1,1,50000]])))
    new_prediction = (new_prediction > 0.5)

# EVALUATE, IMPROVE, TUNNING --------------------------------------------------
def Experiment_Classifier(optimizer, loss):
    classifier = Sequential()
    classifier.add(Dense(units=6, kernel_initializer='uniform', activation='relu', input_dim=11))
    classifier.add(Dropout(rate = 0.05))
    classifier.add(Dense(units=6, kernel_initializer='uniform', activation='relu'))
    classifier.add(Dense(units=1, kernel_initializer='uniform', activation='sigmoid'))   
    classifier.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])
    return classifier

def kxValidation(classifier): 
    # Kcross validation 10 folds = train model 10 times
    classifier = KerasClassifier(build_fn = Experiment_Classifier, batch_size=192, epoches=100)
    accuracies = cross_val_score(estimator = classifier, X = data[0], y = data[2], cv=10, n_jobs=-1)
    mean = accuracies.mean()
    variance = accuracies.std()
    
def gridSearchCV(classifier):
    # GridSearchCV finds the best parameters yields highest accuracy
    grid_search = GridSearchCV(estimator = classifier, param_grid = parameters, 
                               scoring = 'accuracy', cv = 10)
    grid_search = grid_search.fit(data[0], data[2])
    #best_parameter = grid_search.best_params_
    #best_accuracy = grid_search.best_score_
    return grid_search
    
start_time = time.time()
data = DataPreprocessing()
classifier = KerasClassifier(build_fn = Experiment_Classifier)
# Dictionary of hyper parameters
parameters = {'batch_size':[96], 'epochs':[100], 'optimizer':['adam'], 'loss':['binary_crossentropy']}
gscv=gridSearchCV(classifier)
print("%s seconds" %(time.time() - start_time))
# Save model
model_backup_path = '/home/turbo-octo-potato/Deep_Learning_A_Z/SupervisedDeepLearning/Artificial_Neural_Network_ANN/model.h5'
gscv.best_estimator_.model.save(model_backup_path)
print("Model saved to", model_backup_path)
#11-6-6-1 no dropout, loss=binary_crossentropy, batch_size 25, epochs 500, adam, 84.6375%
#11-6-6-1 0.15dropout, loss=poisson, batch_size 192, epochs 50, adam, 80.4% 773.7297103404999 seconds
