# Dices roll simulation, number of sides are up to the user
import random
import os
import json
import Winmouse

#FolderName = 'DataStore' #same directory as main file
FileName = 'DataStore'
FileType = '.json'

# Get number of dice in this simualation
def Dices():
    while True:     #input range num check
        while True: #input type num check
            try:
                Dices = input("How many dice do you want to have?: (1-5)")
                Dices = int(Dices)
                break
            except ValueError:
                print("Expect a number than",Dices)
        if (Dices > 5) or (Dices < 1):
            print ("I was not expecting this number", Dices)
        else:
            print ("You want to have", Dices, "dice(s).")
            return Dices
            break

# Get user input for the dice name
def DicesName(NumOfDices):
    DiceNameList = []
    for num in range(NumOfDices):
        while True:
            try:
                DiceName = str(input("Give it a name: "))
                if not DiceName:
                    raise ValueError("Empty input")
                else:
                    DiceNameList.append(DiceName)
                    break
            except ValueError as e:
                print(e)
    return DiceNameList

# Get user input for dice number range
def SidesRange():
    while True:     #input range num check
        while True: #input RangeMin check
            try:
                RangeMin = input("What will be your dice min range?: (1-99)")
                RangeMin = int(RangeMin)
                break
            except ValueError:
                print("Expect a number than",RangeMin)
        while True: #input RangeMax check
            try:
                RangeMax = input("What will be your dice max range?: (1-99)")
                RangeMax = int(RangeMax)
                break
            except ValueError:
                print("Expect a number than",RangeMax)
                
        if (RangeMin > 99 or RangeMax > 99) or (
            RangeMin < 1 or RangeMax < 1):
            print ("I was not expecting this number range", RangeMin,
                   "to", RangeMax)
        else:
            print ("You want to have the range of", RangeMin, "to",
                   RangeMax)
            return (RangeMin, RangeMax)
    
# Random roll on each dice
def SidesNumGen(RangeMin, RangeMax, Sides):
    SidesNumList = []
    for num in range (Sides):
        ranNum = random.randint(RangeMin,RangeMax)
        SidesNumList.append(ranNum)
    return SidesNumList

# Get user input for the number of dice sides
def DicesSideAndNumber(NumOfDices, NameOfDices):
    DiceSideList = []
    for num in range(NumOfDices):
        while True: #input type num check
            try:
                DiceSide = input("How many side do you want?: (1-99)")
                DiceSide = int(DiceSide)
                break
            except ValueError:
                print("Expect a number than",DiceSide)
        if (DiceSide > 99) or (DiceSide < 1):
            print ("I was not expecting this number", DiceSide)
        else:
            print ("You want to have", DiceSide, "side(s) for", NameOfDices[num])
            RangeMin, RangeMax = SidesRange()
            DiceSideList.append(SidesNumGen(RangeMin, RangeMax, DiceSide))
    return DiceSideList

# Set Dices data to JSON
def DataToJson(Name, Side):
    dirname, filename = os.path.split(os.path.abspath(__file__))
    d = {} #Dictionary format, key -> value
    d["Name"] = Name
    d["Side"] = Side
    fp = open(dirname+"\\"+FileName+FileType,'w')
    json.dump(d, fp, ensure_ascii = False, indent = 4)
    fp.close()

# Get Dices data from JSON
def DataFromJson():
    dirname, filename = os.path.split(os.path.abspath(__file__))
    d = {}
    with open(dirname+"\\"+FileName+FileType,'r') as fp:
        d = json.load(fp)
    NameOfDices = d["Name"]
    SidesAndNumberOfDices = d["Side"]
    return (NameOfDices, SidesAndNumberOfDices)

# Get the dice to play
def setPlayParameters():
    Name, Side = DataFromJson()
    print ("Select the dices to play with (",Name,")")
    while True:
        try:
            DiceSelected = str(input("Dice Name: "))
            if not DiceSelected:
                raise ValueError("Empty input")
            elif DiceSelected in Name:
                DiceIndex = Name.index(DiceSelected)
                Side = Side[DiceIndex]
                print ("Selected dices sides are (",Side,")")
                break
            else:
                print ("Dice is not in the list")
        except ValueError as e:
            print(e)
    return (Side)

# Overwrite current dice parameter in the JSON file
def setDiceParameters():
    Number = Dices()
    Name = DicesName(Number)
    SidesAndNumber = DicesSideAndNumber(Number, Name)
    DataToJson(Name, SidesAndNumber)

# IAOI this runs when is the primary module
#if __name__ == "__main__":
#    setDiceParameters()

# Run the below to start playing
Side = setPlayParameters()
while True:
    Winmouse.inp.mi.dwFlags = Winmouse.MOUSEEVENTF_LEFTDOWN
    Winmouse.send_input_func(1, Winmouse.ctypes.pointer(Winmouse.inp),
                             Winmouse.sizeof(Winmouse.INPUT))
    print (random.choice(Side))
