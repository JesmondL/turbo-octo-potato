import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
import json, os, sqlite3

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)
    return None

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
        self.jsonStock = {}

    def getAll(self):
        with open('stock.json') as f:
            self.jsonStock = json.load(f)
        return self.jsonStock

    def writeDB(self):
        conn = create_connection('stock.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE stocks(date text, trans text, symbol text, qty real, price real)''')
        conn.commit()
        conn.close()

    def readDB(self):
        conn = create_connection('stock.db')
        c = conn.cursor()
        c.execute("""SHOW TABLES""")
        results = c.fetchall()
        results_list = [item[0] for item in results] # Conversion to list of str
        return results_list

    def updateDB(self):
        return "Success"

    def deleteDB(self):
        return "Success"  

#a = DBactions()
#a.getAll()
#b = Ticker((list(a.results.keys())[0]), list(a.results.values())[0])