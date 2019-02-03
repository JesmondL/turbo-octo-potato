# -*- coding: utf-8 -*-
"""
Author: Jesmond Lee
Date: 02.02.2019
Python 3.6

RNN is used for time series analysis.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, TensorBoard

dataset_train = pd.read_csv('Z74.SI_history.csv')
sc = MinMaxScaler(feature_range = (0,1)) # normalize data to between 0-1
n_future = 20  # Number of days want to predict into the future
n_past = 60  # Number of past days want to use to predict the future
n_feature = 4 # Number of features want to predict
X_train = []
Y_train = []

# DATA PROCESSING -------------------------------------------------------------
def DataPreprocessing(dataset_train, X_train, Y_train):
    # get data in column 1 and create a numpy array
    training_set = dataset_train.iloc[:, 1:2].values
    # sc = MinMaxScaler(feature_range = (0,1)) # normalize data to between 0-1
    training_set_scaled = sc.fit_transform(training_set)
    # predict next 1 output
    for i in range (n_past, len(dataset_train)):
        # memorized num of past data (n_past) for prediction, 0 to n_past
        X_train.append(training_set_scaled[i-n_past:i, 0])
        # exclude past data info, RNN will use to predict the incoming n_past
        Y_train.append(training_set_scaled[i, 0])
    X_train, Y_train = np.array(X_train), np.array(Y_train)
    # reshape - add a dimension to np array
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    return X_train, Y_train
    
def DataPreprocessing_Multi(dataset_train, X_train, Y_train):
    # Select the range of column data category wish to process
    cols = list(dataset_train)[1:5]
    # Preprocess data for training by removing all commas
    dataset_train = dataset_train[cols].astype(str)
    for i in cols:
        for j in range(0,len(dataset_train)):
            dataset_train[i][j] = dataset_train[i][j].replace(",","")
    dataset_train = dataset_train.astype(float) # change from string to float type
    training_set = dataset_train.as_matrix() # ndarray, each column is a data category
    #sc = MinMaxScaler(feature_range = (0,1)) # normalize data to between 0-1
    training_set_scaled = sc.fit_transform(training_set) # scale data to between 0-1
    sc_predict = MinMaxScaler(feature_range=(0,1))
    sc_predict.fit_transform(training_set[:,0:1])

    for i in range(n_past, len(training_set_scaled) - n_future + 1):
        X_train.append(training_set_scaled[i - n_past:i, 0:5])
        Y_train.append(training_set_scaled[i + n_future - 1:i + n_future, 0])
    X_train, Y_train = np.array(X_train), np.array(Y_train)
    return X_train, Y_train, sc_predict
    
# INITIALIZE RNN --------------------------------------------------------------
def create_RNN(X_train, activation, n_feature):
    regressor = Sequential()
    # add LSTM layer and dropout regularisation. low unit difficult to capture trends
    regressor.add(LSTM(units = 50, return_sequences = True, input_shape = (n_past, n_feature))) # single data
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units = 50, return_sequences = True)) # 2nd layer
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units = 50, return_sequences = True)) # 3rd layer
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units = 50, return_sequences = False)) # 4th layer
    regressor.add(Dropout(0.2))
    # output layer
    regressor.add(Dense(units = 1, activation=activation))
    # complie 
    regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')
    return regressor
    
# TRAINING RNN ----------------------------------------------------------------
def train_RNN(regressor, X_train, Y_train):
    regressor.fit(X_train, Y_train, epochs = 100, batch_size = 192)
    dataset_test = pd.read_csv('Z74.ST_test.csv')
    # get data in column 1 and create a numpy array
    real_stock_price = dataset_test.iloc[:, 1:2].values
    # get predicted stock price of future. vertical concat axis=0
    dataset_total = pd.concat((dataset_train['Open'], dataset_test['Open']),
                              axis = 0)
    # previous 60 days till last settle day data as inputs
    inputs = dataset_total[len(dataset_total)-len(dataset_test) - n_past:].values
    # reshape the input to np array 
    inputs = inputs.reshape(-1,1)
    # normalize data to between 0-1
    inputs = sc.fit_transform(inputs)
    X_test = []
    # test set only has 20 days, hence 60 to 80
    for i in range (n_past, n_past+n_future):
        # append 60 data from column 0
        X_test.append(inputs[i-n_past:i, 0])
    X_test = np.array(X_test)
    # reshape - add a dimension to np array
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    predicted_stock_price = regressor.predict(X_test)
    predicted_stock_price = sc.inverse_transform(predicted_stock_price)
    
    # Save model
    regressor.save('model.h5')
    
    return real_stock_price, predicted_stock_price
    
def train_RNN_multi(regressor, X_train, Y_train, sc_predict):
    es = EarlyStopping(monitor='val_loss', min_delta=1e-10, patience=10, verbose=1)
    rlr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, verbose=1)
    mcp = ModelCheckpoint(filepath='weights.h5', monitor='val_loss', verbose=1, save_best_only=True, save_weights_only=True)
    tb = TensorBoard('logs')
    history = regressor.fit(X_train, Y_train, shuffle=True, epochs=100,
                        callbacks=[es, rlr,mcp, tb], validation_split=0.2, verbose=1, batch_size=192)
    #Predicting on the training set and plotting the values. the test csv only has 20 values and
    # "ideally" cannot be used since we use 60 timesteps here.
    predictions = regressor.predict(X_train)
     
    #predictions[0] is supposed to predict y_train[19] and so on.
    predicted_stock_price = sc_predict.inverse_transform(predictions[0:-20])
    real_stock_price = sc_predict.inverse_transform(Y_train[19:-1])
        
    # Save model
    regressor.save('model.h5')
    
    return real_stock_price, predicted_stock_price
    
data = DataPreprocessing_Multi(dataset_train, X_train, Y_train) # multi data predict
#data = DataPreprocessing(dataset_train, X_train, Y_train) # single data predict
rnn = create_RNN(data[0], 'sigmoid', n_feature)
trained_rnn = train_RNN_multi(rnn, data[0], data[1], data[2]) # multi data train
#trained_rnn = train_RNN(rnn, data[0], data[1]) # single data train
plt.plot(trained_rnn[0], color = 'red', label = 'Real Stock Price')
plt.plot(trained_rnn[1], color = 'blue', label = 'Predicted Stock Price')
plt.title('Stock Price Prediction')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.show()