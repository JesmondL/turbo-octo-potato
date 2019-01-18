import sys
import os.path

def UserInput(question):
    while True:
        Input = input(question)
        if os.path.isfile(Input):
            return Input
            break
        elif os.path.isdir(Input) == False:
            print("Directory is not valid")
        elif os.path.isfile(Input) == False:
            print("File is not valid")
        
def OpenFile(FilePath):
    try:
        if os.access(FilePath, os.R_OK): # OS file read OK
            File = File.open(FilePath)
        else:
            print("Unable to read file")
    except IOError as e:
        for Arg in e.args:
            print(Arg)  # Exception in str only
        for Entry in dir(e):    # go through the list of errors
            if(not Entry.startswith("_")):
                try:
                    print(Entry, " = ", e.__getattribute__(Entry))
                except AttributeError:
                    print("Attribute ", Entry, " not acessible")

def UserLoadFile():
    try:
        OpenFile(UserInput("Please enter your input : "))
    except:
        print("exeption in userloadfile function")
    
