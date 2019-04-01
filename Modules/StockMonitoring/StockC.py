"""triggers something in model to show in view
handling the user interface and application"""

#CTL+SHIFT+P python interpretor to webscraping
#pip install required package
# https://sg.finance.yahoo.com/quote/Z74.SI/history?period1=1262275200&period2=1546358400&interval=1d&filter=history&frequency=1d

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
import StockM, StockV
import time, json, requests, datetime

def createTicker(mTK, tickers):
   """ Create ticker obj in db """
   list_tickers_obj = []
   for ticker in tickers:
      setattr(mTK, 'name', ticker)
      setattr(mTK, 'symbol', tickers[ticker])
      list_tickers_obj.append(mTK)
   return list_tickers_obj

def readTicker(mDB):
   """ Read ticker obj in db """
   return True

def updateTicker(tickers):
   """ Update ticker obj to db """
   return True

def deleteTicker(tickers):
   """ Delete ticker obj in db """
   return True
   
if __name__ == "__main__":
   StockV.startView()

   mDB = StockM.actionsDB() # db object
   tickers_json = mDB.readDB()
   jsonYmap= StockM.loadJSON('yahoo_map.json')
   db = StockM.create_connection('stock.db')

   while (int(datetime.datetime.now().hour) >= int(mDB.jsonStock['Singapore_Time']['open'])) & \
      (int(datetime.datetime.now().hour) <= int(mDB.jsonStock['Singapore_Time']['close'])) & \
         (datetime.datetime.now().weekday() <= 5): # weekends will be FALSE
      for ticker in mDB.jsonStock['Singapore_Stock']:
         scraps = StockM.scrapWeb(mDB.jsonStock['Singapore_Stock'][ticker], jsonYmap)
         StockV.scrappedView(ticker)
         #name, symbol, date, time, value
         StockM.create_ticker(name, symbol, date, time, value)
         mDB.writeDB(scraps)

         time.sleep(5)
   db.close()
   StockV.endView(datetime.datetime.weekday(), datetime.datetime.now().hour)
