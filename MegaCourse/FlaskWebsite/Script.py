# -*- coding: utf-8 -*-
"""
Created on Sat May  5 21:36:13 2018

@author: jemond
"""

#sudo pip3 install flask
#http://localhost:5000/
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')#home page
def home():
    return render_template("home.html")
    
@app.route('/about/')#about page
def about():
    return render_template("about.html")
    
if __name__=="__main__":
    app.run(debug=True)