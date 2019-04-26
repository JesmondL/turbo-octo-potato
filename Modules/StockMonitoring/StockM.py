"""pure application logic, which interacts with the database. 
It includes all the information to represent data to the end user.
handling data and business logic"""

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
import json, os, sqlite3, urllib.request, requests, re
from bs4 import BeautifulSoup # for html parsing and scraping
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer

sc_predict = MinMaxScaler(feature_range = (0,1)) # normalize data to between 0-1, combo with sigmod
sc = sc_predict
n_past = 50  # Number of past days want to use to predict/ timesteps
n_future = 2 # Number of days predict into future
n_feature = 1

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
    try:
        with open(fp) as f:
            jsonObj = json.load(f)
        return jsonObj
    except Exception as e:
        print (e)
        return

def scrapWeb(ticker, jsonYmap):
    try:
        page = urllib.request.urlopen('https://sg.finance.yahoo.com/quote/%s?p=%s&.tsrc=fin-srch-v1'%(ticker,ticker))
        soup = BeautifulSoup(page, "lxml")
        for index, item in enumerate (jsonYmap):
            if item == "Ticker":
                jsonYmap[item] = soup.find("h1").text
            else:
                jsonYmap[item] = soup.find("td", attrs={"data-test":jsonYmap[item]}).text
        return jsonYmap
    except Exception as e:
        print (e)
        return None

def scrapRealTime(ticker, jsonStInfo, source):
    try:
        page = urllib.request.urlopen('https://sg.finance.yahoo.com/quote/%s?p=%s&.tsrc=fin-srch-v1'%(ticker,ticker))
        soup = BeautifulSoup(page, "lxml")
        return soup.body.find('span', attrs={'class': jsonStInfo['Sources'][source]}).text
    except Exception as e:
        print (e)
        return None

def scrapAPI(purpose, ticker):
    try:
        yahoo_api = "https://query2.finance.yahoo.com/v11/finance/quoteSummary/{0}?formatted=true&lang=en-US&modules={1}".format(ticker.symbol, purpose)
        yahoo_api_response = requests.get(yahoo_api)
        yahoo_api_json =  json.loads(yahoo_api_response.text)
        if (yahoo_api_json["quoteSummary"]["error"] == None):
        # Open,High,Low,Close

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
            # with open(ticker.symbol+".csv", "a") as file:
            #     file.write(str(rOpen)+","+str(rHigh)+","+str(rLow)+","+str(rClose)+"\n")
            return [str(rOpen),str(rHigh),str(rLow),str(rClose)]
        else:
            print("API error: {0}".format(yahoo_api_json["quoteSummary"]["error"]))
            return None
    except Exception as e:
        print (e)
        return None

def create_daily_record(sName, sSymbol, sDate, sTime, sValue):
    try:
        with open("Daily/"+sSymbol+"_"+sDate+".csv", "a+") as f:
            f.write(sName+","+sSymbol+","+sDate+","+sTime+","+sValue+"\n")
            f.close()
    except Exception as e:
        return None

def create_closing_record(sSymbol, sDate, sOpen, sClose):
    try:
        with open("History/"+sSymbol+"_history.csv", "a+") as f:
            if sDate in f.read():
                print(sSymbol + " data exist")
            else:
                sDelta = float(sOpen)-float(sClose)
                f.write(sDate+","+str(sOpen)+","+str(sClose)+","+str(sDelta)+"\n")
                f.close()
    except Exception as e:
        return None

def read_daily_record(sSymbol, sDate):
    try:
        rec = pd.read_csv("Daily/"+sSymbol+"_"+sDate+".csv", sep=',',\
            header=None, names = ["Name","Symbol","Date","Time","Value"])
        if len(rec.index) >= n_past:
            return rec
        else:
            return pd.DataFrame()
    except Exception as e:
        print (e)
        return pd.DataFrame()

def prediction(regressor, inputData):
    X_inputData = []
    # (1, 50, 1) [rows, timesteps, columns]
    columns = inputData.Value       # get interested column(s)
    columns = columns.astype(float) # cast panda obj to float type
    columns = columns.tail(n_past)  # get most recent data
    inputData = inputData.Value.to_numpy() # Convert to its Numpy-array representation

    X_inputData = np.reshape(inputData, (1, n_past, 1))
    predictions = regressor.predict(X_inputData)
    predicted_stock_price = sc_predict.inverse_transform(predictions)
    return predicted_stock_price

def scrapNews(sSource, sCompany, sDate, jsonStInfo):
    res = {}
    try:
        if "COMPANY" in sSource: # business time format
            sSource = sSource.replace('COMPANY', sCompany)
            # scrap overview page
            page = urllib.request.urlopen(sSource)
            soup = BeautifulSoup(page, "lxml")
            articalList = soup.body.findAll('div', attrs={'class': 'media-body'}) # webpage artical list
            for index, artical in enumerate (articalList):
                if findWholeWord(sCompany)(str(artical)) == None: 
                    continue
                else:       # webpage artical contains company name
                    url = re.findall("<a href=(.*?)>", str(artical))
                    header = artical.find('a').text
                    date = artical.find('time').text
                    body = artical.find('p').text
                    res[str(sCompany)] = url[0]
            # scrap artical page
            page = urllib.request.urlopen(res[str(sCompany)])
            soup = BeautifulSoup(page, "lxml")
            articalDetail = soup.body.findAll('div', attrs={'class': 'body-copy'})
            articalFull = re.findall("<p>(.*?)</p>", str(articalDetail[0]))
            articalFull = ' '.join(articalFull)
            res[str(sCompany)] = articalFull

        elif "SYMBOL" in sSource: # yahoo format
            sSource = sSource.replace('SYMBOL', jsonStInfo['Singapore_Stock'][sCompany])

        return res
    except Exception as e:
        return res

def newsSentiment(source):
    SIA = SentimentIntensityAnalyzer()
    res = SIA.polarity_scores(source)
    return res

def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

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
        self.conn = create_connection('stock.db')

    def writeDB(self, data):
        sql = ''' INSERT INTO tickers(name, symbol, date, time, value)
                VALUES(?,?,?,?,?) '''
        cur = self.conn.cursor()
        cur.execute(sql, data)
        cur.commit()
        return cur.lastrowid

    def readDB(self):
        return "Success"

    def updateDB(self):
        return "Success"

    def deleteDB(self):
        return "Success" 