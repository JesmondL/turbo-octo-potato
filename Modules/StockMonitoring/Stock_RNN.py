# -*- coding: utf-8 -*-
"""
Author: Jesmond Lee
Date: 04.02.2019
Python 3.6

RNN is used for time series analysis.
"""
#https://towardsdatascience.com/stock-prediction-in-python-b66555171a2
#https://github.com/WillKoehrsen/Data-Analysis/tree/master/stocker
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras.models import load_model
from keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, TensorBoard
import os
os.chdir(os.path.dirname(os.path.realpath('__file__')))

dataset_train = pd.read_csv('Modules/StockMonitoring/Z74.SI_history.csv')
dataset_test = pd.read_csv('Modules/StockMonitoring/Z74.SI_test.csv')
sc = MinMaxScaler(feature_range = (0,1)) # normalize data to between 0-1, combo with sigmod
sc_predict = sc
n_past = 50  # Number of past days want to use to predict/ timesteps
n_feature = 4 # Number of features want to predict
hyperParameters = ['sigmoid', 'adam', 'mean_squared_error']
X_train = []
Y_train = []

# DATA PROCESSING -------------------------------------------------------------
def DataPreprocessing(dataset_train, X_train, Y_train):
    # to take everything column, take column 1 (Open) and create a numpy array as python exclude upper bound column
    training_set = dataset_train.iloc[:, 1:2]
    # normalization and transform training_set
    training_set_scaled = sc.fit_transform(training_set)
    # predict next 1 output based on n_past till end of data
    for i in range (n_past, len(dataset_train)): # start loop from n_past onwards till end of dataset
        # memorized n_past range of data at column 0
        X_train.append(training_set_scaled[i-n_past:i, 0])
        # T+1 data at column 0
        Y_train.append(training_set_scaled[i, 0])
    X_train, Y_train = np.array(X_train), np.array(Y_train)
    # X_train with a new dimension that could be ext factor that affect this stock, num of data, n_past, num of indicators
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], n_feature))
    return X_train, Y_train, 0
    
def DataPreprocessing_Multi(dataset_train, X_train, Y_train):
    # Select the range of column data category wish to process
    cols = list(dataset_train)[1:5]
    # cast panda obj to string type
    dataset_train = dataset_train[cols].astype(str)
    # Preprocess data for training by removing all commas
    for i in cols:
        for j in range(0, len(dataset_train)):
            dataset_train[i][j] = dataset_train[i][j].replace(",","")
    dataset_train = dataset_train.astype(float) # cast panda obj to float type
    training_set = dataset_train.as_matrix() # Convert to its Numpy-array representation
    # normalization and transform training_set
    training_set_scaled = sc.fit_transform(training_set) # scale data to between 0-1
    sc_predict.fit_transform(training_set[:,0:1]) #predict the 1st column data; open price

    for i in range(n_past, len(training_set_scaled) - len(dataset_test) + 1):
        X_train.append(training_set_scaled[i - n_past:i, 0:(n_feature + 1)])
        Y_train.append(training_set_scaled[i + len(dataset_test) - 1:i + len(dataset_test), 0])
    X_train, Y_train = np.array(X_train), np.array(Y_train)
    return X_train, Y_train, sc_predict
    
# INITIALIZE RNN --------------------------------------------------------------
def create_RNN():
    regressor = Sequential()
    # num of LSTM /memory unit, ret to next layer true when there is next LSTM, only timestep and feature(s)
    # add LSTM layer and dropout regularisation. low unit difficult to capture trends
    regressor.add(LSTM(units = 50, return_sequences = True, input_shape = (n_past, n_feature)))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units = 50, return_sequences = True)) # 2nd layer
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units = 50, return_sequences = True)) # 3rd layer
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units = 50, return_sequences = False)) # 4th layer
    regressor.add(Dropout(0.2))
    # output layer
    regressor.add(Dense(units = 1, activation=hyperParameters[0]))
    # loss for regression problem
    regressor.compile(optimizer = hyperParameters[1], loss = hyperParameters[2])
    return regressor
    
# TRAINING RNN ----------------------------------------------------------------
def train_RNN(regressor, X_train, Y_train):
    es = EarlyStopping(monitor='val_loss', min_delta=1e-10, patience=10, verbose=1)
    rlr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, verbose=1)
    mcp = ModelCheckpoint(filepath='weights.h5', monitor='val_loss', verbose=1, save_best_only=True, save_weights_only=True)
    tb = TensorBoard('logs')

    history = regressor.fit(X_train, Y_train, shuffle=False, epochs = 100, batch_size = 192,\
        callbacks=[es, rlr,mcp, tb], validation_split=0.2, verbose=1)
    # Save model
    regressor.save('Modules/StockMonitoring/model.h5')
    
# EVULATE RNN ----------------------------------------------------------------
def evulate_RNN(regressor, X_train, Y_train, sc_predict):
    if n_feature == 1:
        # get data in column 1 and create a numpy array
        real_stock_price = dataset_test.iloc[:, 1:2].values
        # combine train and test data, vertical concat axis=0
        dataset_total = pd.concat((dataset_train['Open'], dataset_test['Open']), axis = 0)
        # get data from (offset of test data and n_past days) till last settle day
        inputs = dataset_total[len(dataset_total)-len(dataset_test) - n_past:].values
        # reshape trick 
        inputs = inputs.reshape(-1,1)
        # normalize data to between 0-1
        inputs = sc.fit_transform(inputs)
        X_test = []
        # 
        for i in range (n_past, n_past + len(dataset_test)):
            # append n_past from column 0
            X_test.append(inputs[i-n_past:i, 0])
        X_test = np.array(X_test)
        # X_test with a new dimension that could be ext factor that affect this stock, num of data, n_past, num of indicators
        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], n_feature))
        predicted_stock_price = regressor.predict(X_test)
        predicted_stock_price = sc.inverse_transform(predicted_stock_price)
    else:
        #Predicting on the training set and plotting the values. the test csv only has X values and
        # "ideally" cannot be used since we use n_past timesteps here.
        predictions = regressor.predict(X_train)
        #predictions[0] is supposed to predict y_train[len(dataset_test)-1] and so on.
        predicted_stock_price = sc_predict.inverse_transform(predictions[0:-len(dataset_test)])
        real_stock_price = sc_predict.inverse_transform(Y_train[len(dataset_test)-1:-1])
    return real_stock_price, predicted_stock_price

#data = DataPreprocessing(dataset_train, X_train, Y_train) # single data predict
data = DataPreprocessing_Multi(dataset_train, X_train, Y_train) # multi data predict
if os.path.isfile('Modules/StockMonitoring/model.h5'):
    rnn = load_model('Modules/StockMonitoring/model.h5')
else:
    rnn = create_RNN()
    train_RNN(rnn, data[0], data[1])
result_RNN = evulate_RNN(rnn, data[0], data[1], data[2])
plt.plot(result_RNN[0], color = 'red', label = 'Real Stock Price')
plt.plot(result_RNN[1], color = 'blue', label = 'Predicted Stock Price')
plt.title('Stock Price Prediction')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.show()