# -*- coding: utf-8 -*-
"""
Logistic Regression

Binary output 
"""

#data preprocessing template
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#import dataset that has a binary output [0=no, 1=yes], and correlation data
dataset = pd.read_csv('Social_Network_Ads.csv')
#[the column range to use], will be correlation data 2 = age, 3 = estimated salary
X = dataset.iloc[:, [2,3]].values 
#the column range to use, will be binary output 0=no purchase, 1=purchase
Y = dataset.iloc[:, 4].values 

#split dataset into training and test set
#test_size value of the total data will be the num of test data
#random_state is set to 0 for no random sampling
from sklearn.cross_validation import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, 
  test_size = 0.2, random_state = 0)
 
#feature scaling by removing the mean and scaling to unit variance
from sklearn.preprocessing import StandardScaler
sc_X = StandardScaler()
#fit to data then transform
X_train = sc_X.fit_transform(X_train)
#standardization by centering and scaling
X_test = sc_X.transform(X_test)

#fitting logistic regression to training set
from sklearn.linear_model import LogisticRegression
#random_state same as train data to get the same result
classifier = LogisticRegression(random_state = 0)
classifier.fit(X_train, Y_train )

#predicting the test set results
Y_pred = classifier.predict(X_test)

#confusion matrix, evulate the model accuracy
from sklearn.metrics import confusion_matrix
#top left and bottom right are correct pred, others are wrong
cm = confusion_matrix(Y_test, Y_pred)

#visualising training set results
from matplotlib.colors import ListedColormap
X_set, Y_set = X_train, Y_train #local variables to hold data variables
#column 0 is age and column 1 is salary. Setting min of both parameters as -1
#and max as +1, with resolution of 0.01
X1, X2 = np.meshgrid(np.arange(start = X_set[:, 0].min() -1, stop = X_set[:,0].max() + 1, step = 0.01),
                     np.arange(start = X_set[:, 1].min() -1, stop = X_set[:,0].max() + 1, step = 0.01))
#apply classifer on all the pixles, colorize the pixle points, with contour to
#seperate the region by a contour
plt.contourf(X1, X2, classifier.predict(np.array([X1.ravel(), X2.ravel()]).T).reshape(X1.shape),
             alpha=0.75, cmap = ListedColormap(('red','green')))
plt.xlim(X1.min(), X1.max())
plt.ylim(X2.min(), X2.max())
#make a scatter plot
for i, j in enumerate(np.unique(Y_set)):
    plt.scatter(X_set[Y_set == j, 0], X_set[Y_set == j, 1],
                c = ListedColormap(('red','green'))(i),label = j)
plt.title('Logistic Regression Training set')
plt.xlabel('Age')
plt.ylabel('Estimated salary')
plt.legend()
plt.show()