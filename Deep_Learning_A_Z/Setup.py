# -*- coding: utf-8 -*-
"""
Author: Jesmond Lee
Date: 27/1/2018
Python 3.5

Environment setup prior to the usage of keras
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
#uninstall tensorflow, as keras overwrites tensorflow setting
#install cuda 8.0 from legacy release https://developer.nvidia.com/cuda-toolkit-archive
#sudo dpkg -i cuda-repo-ubuntu1604-8-0-local-ga2_8.0.61-1_amd64.deb
#sudo apt-get install nvidia-390
#sudo apt-get install cuda-8-0 
#install cuDNN v5 for cuda 8.0 https://developer.nvidia.com/rdp/cudnn-archive
#export LD_LIBRARY_PATH=/usr/local/cuda-8.0/lib64/
#export LD_LIBRARY_PATH=/usr/local/cuda/include
#sudo pip3.5 install tensorflow-gpu
#sudo pip3.5 install --upgrade tensorflow-gpu

# Check if GPU has been detected
#import tensorflow as tf
#sess = tf.Session(config=tf.ConfigProto(log_device_placement=True))
