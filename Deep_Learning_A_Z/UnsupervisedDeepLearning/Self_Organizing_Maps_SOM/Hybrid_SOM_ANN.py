# -*- coding: utf-8 -*-
"""
Author: Jesmond Lee
Date: 30/3/2018
Python 3.5

Hybrid deep learning model - SOM + ANN

First part is to perform SOM. Create additional column to mark those IDs with
SOM prediction as fraud. Perform fit_transform of the input data before ANN.

Second part is to perform ANN with original data, SOM predictions of fraud,
a small batch size and epochs is enough for this exercise. Result of the ANN
with the additional analysis from SOM gives y_pred

Third part is to sort the result. The most likely to be acting fraud has the 
highest 2nd col in y_pred
"""

import os
os.chdir('C:\\Users\\jesmond.lee\\Downloads\\') # change working dir
from Self_Organizing_Maps_SOM.Learning_SOM import SOM # import class
from Artificial_Neural_Network_ANN import Learning_ANN as ANN
from sklearn.preprocessing import StandardScaler
import numpy as np

# create an instance and perform SOM
SOM_instance = SOM() 
data = SOM_instance.DataPreprocessing()
trained_SOM = SOM_instance.train_SOM(data[0], data[1])
result = SOM_instance.Evaluate(data[0], trained_SOM)
result = SOM.sc.inverse_transform(result)

# create matrix of feature based on the all the data
customers = data[2].iloc[:,1:].values
# create dependent variables. Pretend all cust didn't cheat. Replace index to 1 for
# all those who is predicted as cheats by SOM
is_fraud = np.zeros(len(data[2])) # initialize all cust as no cheat
for i in range(len(data[2])):
    if data[2].iloc[i,0] in result: # row i, column 0 is cust ID is in SOM fraud result
        is_fraud[i] = 1 # 1=approved
        
customers = SOM.sc.fit_transform(customers)
classifier = ANN.create_ANN(15, 6, 6, 1)
classifier.fit(customers, is_fraud, batch_size = 1, epochs =3)
y_pred = classifier.predict(customers) # probability
# 1st col cust ID, 2nd col predicted probability, horizontal concatenation
y_pred = ANN.np.concatenate((data[2].iloc[:,0:1].values, y_pred), axis = 1) 
# sort array based on 2nd col
y_pred = y_pred[y_pred[:,1].argsort()]
