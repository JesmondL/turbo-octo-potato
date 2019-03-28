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

    def readDB(self):
        conn = create_connection('stock.db')

        c = conn.cursor()
        c.execute("""SHOW TABLES""")
        results = c.fetchall()
        results_list = [item[0] for item in results] # Conversion to list of str
        return results_list
        
    def writeDB(self):
        conn = create_connection('stock.db')
        db_table = readDB()
        if table in db_table:
             continue
        else:
            # Create table
            c.execute('''CREATE TABLE stocks(date text, trans text, symbol text, qty real, price real)''')
            conn.commit()
        except Exception as e:
            print (e)
        conn.close()

#a = DBactions()
#a.getAll()
#b = Ticker((list(a.results.keys())[0]), list(a.results.values())[0])