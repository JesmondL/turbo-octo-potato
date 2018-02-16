# -*- coding: utf-8 -*-
"""
Author: Jesmond Lee
Date: 22/1/2018
Python 3.5

Import the historical data (larger historical data higher accuracy) and getting
the opening price of the day to predict. Data needs to be scaled and transformed
to the range of 0 to 1 with MinMaxScaler fit transform.

Timestep of 60days, taking 1 month = 20 working days (larger timestep could 
improve the prediction). X_train will be used as the RNN memory and rest of the
train data will be used to train. Numpy array requires 3D array, reshape to 
meet criteria. 

RNN of 4 layers (larger layer could have different results), taking the input 
from X_train. Higher LSTM neurons value can react to the complexity of the
problem (experiment to see results).

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout

dataset_train = pd.read_csv('/home/turbo-octo-potato/Deep_Learning_A_Z/SupervisedDeepLearning/Recurrent_Neural_Networks_RNN/Google_Stock_Price_Train.csv')
sc = MinMaxScaler(feature_range = (0,1))
# DATA PROCESSING -------------------------------------------------------------
def DataPreprocessing():
    # get data in column 1 and create a numpy array
    training_set = dataset_train.iloc[:, 1:2].values
    # normalize data to between 0-1
    #sc = MinMaxScaler(feature_range = (0,1))
    training_set_scaled = sc.fit_transform(training_set)
    # data structure with 60 timestep to predict next 1 output
    X_train = []
    Y_train = []
    for i in range (60, 1258):
        # get first 60 days before financial day from column 0, memorized for prediction
        X_train.append(training_set_scaled[i-60:i, 0])
        # exclude 60 days info, RNN will use to predict the incoming 61-1258
        Y_train.append(training_set_scaled[i, 0])
    X_train, Y_train = np.array(X_train), np.array(Y_train)
    # reshape - add a dimension to np array
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    return X_train, Y_train

# INITIALIZE RNN --------------------------------------------------------------
def create_RNN(X_train):
    regressor = Sequential()
    # add LSTM layer and dropout regularisation. low unit difficult to capture trends
    regressor.add(LSTM(units = 50, return_sequences = True, input_shape = (X_train.shape[1],1)))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units = 50, return_sequences = True))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units = 50, return_sequences = True))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units = 50))
    regressor.add(Dropout(0.2))
    # output layer
    regressor.add(Dense(units = 1))
    # complie 
    regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')
    return regressor
    
# TRAINING RNN ----------------------------------------------------------------
def train_RNN(regressor, X_train, Y_train):
    regressor.fit(X_train, Y_train, epochs = 100, batch_size = 192)
    dataset_test = pd.read_csv('/home/turbo-octo-potato/Deep_Learning_A_Z/SupervisedDeepLearning/Recurrent_Neural_Networks_RNN/Google_Stock_Price_Test.csv')
    # get data in column 1 and create a numpy array
    real_stock_price = dataset_test.iloc[:, 1:2].values
    # get predicted stock price of 2017. vertical concat axis=0
    dataset_total = pd.concat((dataset_train['Open'], dataset_test['Open']),
                              axis = 0)
    # previous 60 days till last settle day data as inputs
    inputs = dataset_total[len(dataset_total)-len(dataset_test) - 60:].values
    # reshape the input to np array 
    inputs = inputs.reshape(-1,1)
    # normalize data to between 0-1
    inputs = sc.fit_transform(inputs)
    X_test = []
    # test set only has 20 days, hence 60 to 80
    for i in range (60, 80):
        # append 60 data from column 0
        X_test.append(inputs[i-60:i, 0])
    X_test = np.array(X_test)
    # reshape - add a dimension to np array
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    predicted_stock_price = regressor.predict(X_test)
    predicted_stock_price = sc.inverse_transform(predicted_stock_price)
    return real_stock_price, predicted_stock_price
    
data = DataPreprocessing()
rnn = create_RNN(data[0])
trained_rnn = train_RNN(rnn, data[0], data[1])
plt.plot(trained_rnn[0], color = 'red', label = 'Real Google Stock Price')
plt.plot(trained_rnn[1], color = 'blue', label = 'Predicted Google Stock Price')
plt.title('Google Stock Price Prediction')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.show()
# unable to react to fast non linear change