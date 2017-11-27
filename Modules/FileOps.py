# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 20:19:09 2017

@author: Jesmond
"""
#https://developers.google.com/edu/python/lists

file = open("fruits.txt",'r') #type(file) io.TextIOWrapper
content = file.read() #type(content) str
#Reading cause the pointer to be at the last of the file.
#Moves the read pointer to the 0th position to allow iterate through again
file.seek(0)
content2 = file.readlines() #type(content2) list 

#list comprehension method
#rstrip removes unwanted string in the list
#remove \n next line in the list 
content2 = [i.rstrip("\n") for i in content2]
#unclosed file will not have written content be saved
file.close()
#count the string length in each list entry
content3 = [len(i) for i in content2]

#open and create the file if is not exist. Only can write str type and have to 
#write everything in 1 session
file = open("fruits.txt",'w')
content = ["apple","banana","coconut"]
content2 = [str(len(i)) for i in content]
content3 = content + content2
[file.write(i) for i in content3]
file.close()

#opens the file with pointer at the last entry
file = open("fruits.txt",'a')
file.write("last entry")
file.close()

#with allow to write and save without close()
with open("fruits.txt",'a+') as file:
    file.seek(0)
    content = file.read()
    file.write("\n EOL")
    
#Exerise 1
temperatures = [10,-20,-289,100]
def c_to_f(temperatures):
    with open("temp.txt",'w') as file:
        for c in temperatures:
            if c < -273.15:
                file.write("invalid \n")
            else:
                f = c*9/5+32
                file.write(str(f) + "\n")

c_to_f(temperatures)    