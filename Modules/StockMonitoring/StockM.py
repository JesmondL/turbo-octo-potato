import json, os

class Ticker(object):
    def __init__(self):
        self.name = None
        self.symbol = None
        # self.previousclose = None
        # self.open = None
        # self.bid = None
        # self.ask = None
        # self.dayRange = None
        # self.weekRange = None
        # self.volume = None
        # self.avgVolume = None
        # self.marketCap = None
        # self.beta = None
        # self.peRatio = None
        # self.eps = None
        # self.earning = None
        # self.dividend = None
        # self.exDividendDTE = None
        # self.yrTargetEst = None
		
class DBactions(object):
    def __init__(self):
        self.results = {}
    #returns all tickers inside db.txt
    def getAll(self):
        with open ('StockList.txt', 'r') as file:
            for line in file:
                line = line.split(',', 3)
                self.results[line[0]]= line[1]
        return self.results

    #update stock name/ symbol to db.txt
    def updateOne(self):
        return "Success"  

#a = DBactions()
#a.getAll()
#b = Ticker((list(a.results.keys())[0]), list(a.results.values())[0])