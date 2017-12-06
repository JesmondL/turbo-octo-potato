# -*- coding: utf-8 -*-
"""
Created on Sun Dec  3 20:47:37 2017

@author: Jesmond

1. input VS lower case dict_keys
2. input VS title case dict_keys
3. input VS upper case dict_keys
4. closet match dict_keys

"""
import json
#from difflib import SequenceMatcher
from difflib import get_close_matches

def translate(word):
    #uncap word match
    if word.lower() in data:
        return data[word.lower()]
    #title match
    elif word.title() in data:
        return data[word.title()]
    #caps word match
    elif word.upper() in data:
        return data[word.upper()]
    #close enough match word
    elif len(get_close_matches(word,data.keys())) > 0:
        yn = input("Did you mean %s instead? Enter Y for yes, or N for no: "
                   %get_close_matches(word, data.keys())[0])
        if yn.lower() == "y":
            return data[get_close_matches(word, data.keys())[0]]
        elif yn.lower() == "n":
            return "Word does not exist"
        else:
            return "Invalid input"
    #doesn't match any word
    else:
        return "Word does not exist"


data = json.load(open("data.json", 'r'))
word = input("Enter word: ")
output = (translate(word))

if type(output) == list:
    for item in output:
        print [item]
else:
    print (output)
    
#compare between 2 words and return a match %
#SequenceMatcher(None,"Rainn","Rain").ratio()
#return a list of most similiar word based on cutoff ratio, 1st = highest
#get_close_matches("rain",data.keys())[0]
