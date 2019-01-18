varNum = 9
print (bin(varNum)) # Binary
print (oct(varNum)) # Octo
print (hex(varNum)) # Hexcial
print (varNum>10)   # Boolean return true
print (varNum<10)   # Boolean return false
print (str(varNum)) # Convert number to string
print (ord(str(varNum))) # Convert 1 string to number in memory
print (int(str(varNum))) # Convert string to number

import datetime
print (str(datetime.datetime.now().date()))
print (str(datetime.datetime.now().time()))

print ("a">"A")     # Compare in string numeric value than character

# Ternary operator
# Condition is evaluated and return a boolean value.
varConditionTrue = (1==1)
varConditionFalse = (1!=1)
print ("true return value" if varConditionTrue else "false return value")
print (("false return value", "true return value") [varConditionFalse])

print (1+1) # Addition
print (1-1) # Subtraction
print (1*1) # Multiply
print (1/2) # Division
print (11%3) # Remainder
print (2**2)# Exponential
print (11//2)# Divison floor

# and, or, not
# bitwise &, |, ^, ~, <<, >>
# assignment +=, -=, *=, /=, %=, **=, //=

# membership In, not in. Valid usecase: database search routine
print ("hello" in "hello world")
print ("bye bye" not in "hello world")

# identity Is, is not. Valid usecase: type check
print (type(2) is int)
print (type(2) is not int)

# Function definition
def Function1(varNum):
    print ("nein funktion")
    print (varNum)
def Function2(varNum = 2):
    print (varNum)
def Function3(FixArg, *Args):
    print ("Passed in ", FixArg)
    for Arg in Args:
        print(Arg)
def FunctionReturn(varA, varB):
    return varA + varB

# User input
Name = input("Enter something: ")
print ("Guten tag", Name)

# ifelse, elseif
if (varNum > 10) or (type(varNum) is int):
    print ("Okay", varNum)
else:
    print ("Not okay", varNum)
if (varNum > 5) and (type(varNum) is str):
    print ("input is greater than 5 and str type")
elif (varNum == 2) and (type(varNum) is str):
    print ("input is 2 and str type")
elif (type(varNum) is int):
    print ("input is int")
else:
    print ("No condition fulfil")

# loop
varNum = 1
for var in "Variable~":
    print ("Alphabat ", varNum, " is ", var)
    varNum+=1
    if varNum > 5:
        print("Stopped at 5th alphabat")
        break
## continue bypass specific element silently
## pass bypass specific element aloud
varNum = 1
for var in "Variable~":
    if var == "a":
        continue
        print("a is filtered, not processed")
    elif var == "b":
        pass
        print("b is filtered, not processed")
    print ("Alphabat ", varNum, " is ", var)
    varNum+=1
## while
while varNum < 11:
    print (varNum)
    varNum+=1
    if varNum == 7:
        continue
    elif varNum == 10:
        pass
        print ("Next is last element")
## nested loop
varNumX = 1
varNumY = 1
for varNumX in range (1,5):
    print('{:>4}'.format(varNumX), end=' ') #{:>n} is n spaces away
    while varNumY <=5:
        print('{:>4}'.format(varNumX * varNumY), end=' ')
        varNumY+=1
    print()
    varNumY=1

# Exception handling
try:
    varNum = int(input("Type a number range of 1 to 10 :"))
except (ValueError, KeyboardInterrupt):  # Build in exception name that catch Value type exception
    print("Exception thrown - expect a number")
except IOError as e: # Only this can use as n
    print("Error number: {1}".format(e.errno))
    print("Error text: {text}".format(e.strerror))
except:             # Undefined will be generic error
    print("Unmatched input")
else:
    if (varNum > 0) and (varNum < 11):
        print("OK", varNum)
    else:
        print("Non exception catch thrown - expect from 1 to 10")
