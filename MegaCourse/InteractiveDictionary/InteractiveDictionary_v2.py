# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 19:45:40 2017

@author: Jesmond

Converts dictionary keys to lower case to have insensitive comparision
1. Unicode comparision
- issue with the not matching case would pass
2. input VS lower cased dict_keys
3. closet match dict_keys

"""
import json
from difflib import get_close_matches
import unicodedata
#http://www.unicode.org/versions/Unicode9.0.0/ch03.pdf#G33992

def translate(word):
    #make dict keys all lower case; insenstive to lower, upper, title keys
    for key in data:
        data[key] = [s.lower() for s in data[key]]
        
    #unicode match, but dict_keys needs exact matching word to return result
    if unicodedata.normalize('NFKD',word.lower()) in unicodedata.normalize(
            'NFKD',str(data.keys())):
        return data[word.lower()]

    #lower case dict keys
#    if word.lower() in data.keys():
#        return data[word.lower()]

    #close enough match word
    elif len(get_close_matches(word.lower(),data.keys())) > 0:
        yn = input("Did you mean %s instead? Enter Y for yes, or N for no: "
                   %get_close_matches(word.lower(), data.keys())[0])
        if yn.lower() == "y":
            return data[get_close_matches(word.lower(), data.keys())[0]]
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