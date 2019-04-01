"""pure application logic, which interacts with the database. 
It includes all the information to represent data to the end user.
handling data and business logic"""

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
import json, os, sqlite3, urllib.request
from bs4 import BeautifulSoup # for html parsing and scraping

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

def create_table(conn, ticker):
    cur = conn.cursor()
    # Check if table  does not exist and create it
    cur.execute('''CREATE TABLE IF NOT EXISTS 
        tickers(symbol TEXT PRIMARY KEY, datetime TEXT) VALUES(?,?) ''') 
    cur.commit()
    return cur.lastrowid

def loadJSON(fp):
    jsonObj = {}
    with open(fp) as f:
        jsonObj = json.load(f)
    return jsonObj

def scrapWeb(ticker, jsonYmap):
    page = urllib.request.urlopen('https://sg.finance.yahoo.com/quote/%s?p=%s&.tsrc=fin-srch-v1'%(ticker,ticker))
    soup = BeautifulSoup(page, "lxml")
    # <span class="Trsdu(0.3s) Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(b)" data-reactid="14">2.9900</span>
    for index, item in enumerate (jsonYmap):
        if item == "Ticker":
            jsonYmap[item] = soup.find("h1").text
        else:
            jsonYmap[item] = soup.find("td", attrs={"data-test":jsonYmap[item]}).text

    return jsonYmap

def scrapAPI(purpose, ticker):
   yahoo_api = "https://query2.finance.yahoo.com/v11/finance/quoteSummary/{0}?formatted=true&lang=en-US&modules={1}".format(ticker.symbol, purpose)
   yahoo_api_response = requests.get(yahoo_api)
   yahoo_api_json =  json.loads(yahoo_api_response.text)
   if (yahoo_api_json["quoteSummary"]["error"] == None):
      # Date,Open,High,Low,Close

      # method 1 - object tree
      # json_tree = objectpath.Tree(yahoo_api_json["quoteSummary"]["result"]) #build obj tree
      # rOpen = tuple(json_tree.execute('$..regularMarketOpen.fmt'))
      # rHigh = tuple(json_tree.execute('$..regularMarketDayHigh.fmt'))
      # rLow = tuple(json_tree.execute('$..regularMarketDayLow.fmt'))
      # rClose = tuple(json_tree.execute('$..regularMarketPreviousClose.fmt'))

      # method 2 - direct path
      rOpen = yahoo_api_json['quoteSummary']['result'][0]['price']["regularMarketOpen"]["raw"]
      rHigh = yahoo_api_json['quoteSummary']['result'][0]['price']["regularMarketDayHigh"]["raw"]
      rLow = yahoo_api_json['quoteSummary']['result'][0]['price']["regularMarketDayLow"]["raw"]
      rClose = yahoo_api_json['quoteSummary']['result'][0]['price']["regularMarketPreviousClose"]["raw"]
      #time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1347517370))
      print("API Success {0}".format(ticker.symbol))
      with open(ticker.symbol+".csv", "a") as file:
         file.write(str(rOpen)+","+str(rHigh)+","+str(rLow)+","+str(rClose)+"\n")
   else:
      print("API error: {0}".format(yahoo_api_json["quoteSummary"]["error"]))

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
		
class actionsDB(object):
    def __init__(self):
        self.jsonStock = {}

    def writeDB(self, data):
        sql = ''' INSERT INTO tickers(name, symbol, date, time, value)
                VALUES(?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, data)
        cur.commit()
        return cur.lastrowid

    def readDB(self):
        with open('stock_info.json') as f:
            self.jsonStock = json.load(f)
        return self.jsonStock

    def updateDB(self):
        return "Success"

    def deleteDB(self):
        return "Success" 