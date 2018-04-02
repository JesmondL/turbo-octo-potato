# -*- coding: utf-8 -*-
"""
Author: Jesmond Lee
Date: 30/3/2018
Python 3.5

Hybrid deep learning model - SOM + ANN

First part is to perform SOM

Second part is to perform ANN
"""
import os
os.chdir('/home/turbo-octo-potato/Deep_Learning_A_Z/') # change working dir
from UnsupervisedDeepLearning.Self_Organizing_Maps_SOM import Learning_SOM as SOM
from SupervisedDeepLearning.Artificial_Neural_Network_ANN import Learning_ANN as ANN
from sklearn.preprocessing import StandardScaler

SOM.py

# create matrix of feature based on the all the data
customers = SOM.dataset.iloc[:,1:].values
# create dependent variables
is_fraud = SOM.np.zero(len(SOM.dataset)) # initialize all cust as no cheat
for i in range(len(SOM.dataset)):
    if SOM.dataset.iloc[i,0] in SOM.frauds: # row i, column 0 is cust ID is in SOM fraud result
        is_fraud[i] = 1 # 1=approved
        
sc = StandardScaler()
customers = sc.fit_transform(customers)
classifier = ANN.create_ANN(15, 6, 6, 1)
ANN.train_ANN(classifier)