# -*- coding: utf-8 -*-
"""
Author: Jesmond Lee
Date: 11/3/2018
Python 3.5

SOM is used for feature detection. Reduce the high numbers of data columns (categories) into a 2D map

https://glowingpython.blogspot.sg/2013/09/self-organizing-maps.html

K cluster - choose the number of K of cluster
select random K point as centroid (random data point/ place in area)
assign each data point to the closest centroid
compute and place new centroid of each cluster
reassign each data point to new closest centroid

Create a grid consist of nodes with a weight vector of n_feature. Randomly initialize
the weight close to 0. Select 1 random observation point in data. Compute the 
Euclidean distance from this point to different neurons in the network. Select
the neuron (winning node) that has the minimum distance to the point. Update
the winning node weight. Gaussian neighbourhood function of mean on winning node,
update weight of winning neighbour neurons. Neighbourhood are is the sigma of 
Gaussian function.

First part is getting the range of column as input (X) to the SOM and a column of
output (Y) that needs to be analyzed. Feature scale the input data to be between 
0-1 and output is not required as is currently 0 or 1.

Second part is training the SOM where a grid needs to be created with random weights
initialized.

Third part is visualizing the SOM distance map by going through the result (X),
marking the winning node and correlate to column output (Y). Red circles represents
winning node and did not get approved, while green square represents winning node and
got approved.
Customer who are close to 1.0 and are approved (green square) are the cases need
to examine as they are the highest chance of fraud.

Fourth part is extract personnel who has highest chance of fraud. Combine the SOM
result to the input table. From the map, we can extract the coordinates of 
people who are in the zone.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

class SOM(object):    
    def __init__(self):
        SOM.sc = MinMaxScaler(feature_range = (0, 1))
        SOM.path = 'C:\\Users\\jesmond.lee\\Downloads\\Self_Organizing_Maps_SOM\\'

# DATA PROCESSING--------------------------------------------------------------
    @staticmethod # do not have any info about the class
    def DataPreprocessing():
        # Importing the dataset
        dataset = pd.read_csv(SOM.path+'Credit_Card_Applications.csv')
        X = dataset.iloc[:, :-1].values # Input, customer information
        Y = dataset.iloc[:, -1].values # Outcome, approved or not
        
        # Feature Scaling input to range of 0 to 1
        X = SOM.sc.fit_transform(X)
        return X,Y,dataset
    
# TRAINING SOM ----------------------------------------------------------------
    @staticmethod # do not have any info about the class
    def train_SOM(X, Y): 
        from Self_Organizing_Maps_SOM.minisom import MiniSom
        # create a 10x10 grid with 15 columns input, update area of 1 WRT winning neuron 
        # neighbours and SOM convergence rate
        som = MiniSom(x = 10, y = 10, input_len = 15, sigma = 1.0, learning_rate = 0.5)
        som.random_weights_init(X) # random initialize weights to the input
        som.train_random(data = X, num_iteration = 100)
        
        # Visualizing the results
        from pylab import bone, pcolor, colorbar, plot, show
        bone() # initialize empty window
        pcolor(som.distance_map().T) # MIT metrics
        colorbar()
        markers = ['o', 's'] # winning node; circle is OK, square is fraud?!
        colors = ['r', 'g'] # red = no approval, green = approval
        for i, x in enumerate(X):   # loop through all rows of input
            w = som.winner(x)       # get winning node of customer 
            plot(w[0] + 0.5,        # winning node X coordinate [0] and Y coordinate [1]
                 w[1] + 0.5,        # offset XY 0.5 to be drawn on the center of the grid
                 markers[Y[i]], # associate markers and y with 0 = no approval as red, 1 = approval as green
                 markeredgecolor = colors[Y[i]],
                 markerfacecolor = 'None', # marker inside color
                 markersize = 10,
                 markeredgewidth = 2)
        show()
        return som
    
# EVALUATE --------------------------------------------------------------------
    @staticmethod # do not have any info about the class
    def Evaluate(X, som):
        som_map = som.distance_map().T
        som_y, som_x = np.where(som.distance_map().T >= 0.95) # get 2D array index of threshold
        som_y = som_y + 1
        som_x = som_x + 1
        
        # Finding the frauds
        mappings = som.win_map(X) # map SOM coordinate XY to the customer profile/input
        win_nodes_mapping=''
        if len(som_x) == 1:
            win_nodes_mapping = 'mappings[(' + str(som_x[0]) + ',' + str(som_y[0]) + ')]'
        else:
            for i in range(len(som_x)):
                if len(mappings[som_x[i],som_y[i]]) != 0:
                    win_nodes_mapping = win_nodes_mapping + ', mappings[(' + str(som_x[i]) + ',' + str(som_y[i]) + ')]'
                else:
                    win_nodes_mapping = win_nodes_mapping
                    # 0 array will remove win XY from list of distance_map().T >= 0.95
                    np.delete(som_x,[i],axis=None)
                    np.delete(som_y,[i],axis=None)
            win_nodes_mapping = win_nodes_mapping[2:] # remove , 
        
        # Get the winning node coordinates from the map. Coordinates changes each time
        # mapping XY cannot be empty and must have same numbers of array if multiples are referred
        #frauds = np.concatenate((win_nodes_mapping), axis = 0) str doesn't work
        #frauds = np.concatenate((mappings[(som_x[0],som_y[0])]), (mappings[(som_x[1],som_y[1])]), axis = 0) # using more than 1 point of reference
        frauds = mappings[(som_x[0],som_y[0])] # single reference
        #frauds = SOM.sc.inverse_transform(frauds) # error at here ValueError: Expected 2D array, got 1D
        return frauds

#data = DataPreprocessing()
#trained_SOM = train_SOM(data[0], data[1])
#result = Evaluate(data[0], trained_SOM)
