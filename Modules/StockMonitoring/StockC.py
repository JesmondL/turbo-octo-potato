#CTL+SHIFT+P python interpretor to webscraping
#pip install required package
# https://sg.finance.yahoo.com/quote/Z74.SI/history?period1=1262275200&period2=1546358400&interval=1d&filter=history&frequency=1d

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
import StockM, StockV
import time, urllib.request, json, requests, objectpath
from bs4 import BeautifulSoup # for html parsing and scraping

def createTicker(tickers):
   """ Create ticker obj in db """
   list_tickers_obj = []
   for ticker in tickers:
      db_Create = StockM.Ticker()
      setattr(db_Create, 'name', ticker)
      setattr(db_Create, 'symbol', tickers[ticker])
      list_tickers_obj.append(db_Create)
   return list_tickers_obj

def readTicker():
   """ Read ticker obj in db """
   db_Read = StockM.DBactions()
   tickers = db_Read.getAll()
   #calls view
   StockV.showAllView(db_Read.results)
   return tickers

def updateTicker(tickers):
   """ Update ticker obj to db """
   return True

def deleteTicker(tickers):
   """ Delete ticker obj in db """
   return True

def scrapWeb(ticker):
   d = {} # data placeholder
   page = urllib.request.urlopen('https://sg.finance.yahoo.com/quote/%s?p=%s&.tsrc=fin-srch-v1'%(ticker.symbol,ticker.symbol))
   soup = BeautifulSoup(page, 'html.parser')
   name_box = soup.find('h1', attrs={'data-reactid':'7'})#title
   left_box = soup.find('div', attrs={'data-test':'left-summary-table'})
   left_box = left_box.find_all('span')
   for c in range (int(len(left_box)/2)):
      d[left_box[c].text] = left_box[c+1].text
   right_box = soup.find('div', attrs={'data-test':'right-summary-table'})
   right_box = right_box.find_all('span')
   for c in range (int(len(right_box)/2)):
      d[right_box[c].text] = right_box[c+1].text
   jd = json.dumps(d)
   #for item in d:
   #   setattr(ticker, ticker[item], d[item])

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

def start():
   tickers = readTicker()
   tickers_obj = createTicker(tickers)
   for ticker_obj in tickers_obj:
      scrapAPI("price", ticker_obj)
      time.sleep(5)
   
if __name__ == "__main__":
   #running controller function
   StockV.startView()
   start()
   StockV.endView()
