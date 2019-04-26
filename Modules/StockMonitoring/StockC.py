"""triggers something in model to show in view
handling the user interface and application"""

#CTL+SHIFT+P python interpretor to webscraping
#pip install required package
# https://sg.finance.yahoo.com/quote/Z74.SI/history?period1=1262275200&period2=1546358400&interval=1d&filter=history&frequency=1d

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
import StockM, StockV
import time, json, requests, datetime, threading, queue, logging, copy
from keras.models import load_model
import pandas as pd

BUF_SIZE = 1
qWebQuery = queue.Queue(BUF_SIZE)
qAnalyticQuery = queue.Queue(BUF_SIZE)
qNewsQuery = queue.Queue(BUF_SIZE)
jsonStInfo= StockM.loadJSON('stock_info.json')
jsonYmap= StockM.loadJSON('yahoo_map.json')

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)

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
   
class ProducerThread(threading.Thread):
   def __init__(self, group=None, target=None, name=None,
   args=(), kwargs=None, verbose=None):
      super(ProducerThread,self).__init__()
      self.target = target
      self.name = name
      self.cnt = 30

   def run(self):
      while True:
         if not qWebQuery.full():
            if (int(datetime.datetime.now().hour) >= int(jsonStInfo['Singapore_Time']['open'])) & \
               (int(datetime.datetime.now().hour) < int(jsonStInfo['Singapore_Time']['close'])) & \
               (datetime.datetime.now().weekday() <= 5): # within operating hour and weekdays will proceed
               gOperating = True
            else:
               gOperating = False
               StockV.noService(datetime.datetime.now().weekday(), datetime.datetime.now().hour)
            qWebQuery.put(gOperating)
            qAnalyticQuery.put(False)
            logging.debug('Putting Web Analytic Query : ' + str(qWebQuery.qsize()) + ' items in queues')
            time.sleep(10)
         if not qNewsQuery.full():
            if self.cnt == 30: # 30*120=3600secs
               qNewsQuery.put(True)
               logging.debug('Putting News Query : ' + str(qNewsQuery.qsize()) + ' items in queues')
               self.cnt = 0
            else:
               self.cnt = self.cnt + 1
      return

class ConsumerThread(threading.Thread):
   def __init__(self, group=None, target=None, name=None,
   args=(), kwargs=None, verbose=None):
      super(ConsumerThread,self).__init__()
      self.target = target
      self.name = name
      return

   def run(self):
      while True:
         if not qWebQuery.empty():
            status = qWebQuery.get()
            logging.debug('Getting RealTime Data : ' + str(qWebQuery.qsize()) + ' items in queue')
            if status:
               for ticker in jsonStInfo['Singapore_Stock']:
                  value = StockM.scrapRealTime(jsonStInfo['Singapore_Stock'][ticker], jsonStInfo, 'yahoo') # get realtime value
                  if value == None:
                     StockV.noRealTimeData()
                  else:
                     # StockV.showRealTimeResult(datetime.datetime.now().strftime("%H:%M"), ticker, value)
                     #name, symbol, date, time, value
                     StockM.create_daily_record(ticker,\
                        jsonStInfo['Singapore_Stock'][ticker], \
                        datetime.datetime.now().strftime("%Y-%m-%d"), \
                        datetime.datetime.now().strftime("%H:%M"), \
                        value)
                  time.sleep(5)
            else:
               for ticker in jsonStInfo['Singapore_Stock']:
                  scraps = StockM.scrapWeb(jsonStInfo['Singapore_Stock'][ticker], jsonYmap.copy())
                  value = StockM.scrapRealTime(jsonStInfo['Singapore_Stock'][ticker], jsonStInfo, 'yahoo')
                  if (scraps == None) or (value == None):
                     StockV.noRealTimeData()
                  else:
                     # Date, Open, Close
                     StockM.create_closing_record(jsonStInfo['Singapore_Stock'][ticker],\
                        datetime.datetime.now().strftime("%Y-%m-%d"), scraps['Open'], value)
                     time.sleep(5)
               StockV.noRealTimeService()
      return

class AnalyticThread(threading.Thread):
   def __init__(self, group=None, target=None, name=None,
   args=(), kwargs=None, verbose=None):
      super(AnalyticThread,self).__init__()
      self.target = target
      self.name = name
      return

   def run(self):
      while True:
         rnn = load_model('model.h5')
         if not qAnalyticQuery.empty():
            status = qAnalyticQuery.get()
            logging.debug('Getting Analysis Trend : ' + str(qAnalyticQuery.qsize()) + ' items in queue')
            if status:
               for ticker in jsonStInfo['Singapore_Stock']:
                  rec = StockM.read_daily_record(jsonStInfo['Singapore_Stock'][ticker], \
                     datetime.datetime.now().strftime("%Y-%m-%d"))
                  if rec.empty:
                     StockV.noAnalyticData(jsonStInfo, ticker)
                  else:
                     result = StockM.prediction(rnn, rec)
                     StockV.showAnalyticResult(result)
            else:
               StockV.noAnalyticService()
      return

class NewsThread(threading.Thread):
   def __init__(self, group=None, target=None, name=None,
   args=(), kwargs=None, verbose=None):
      super(NewsThread,self).__init__()
      self.target = target
      self.name = name
      self.companyList = []
      return

   def run(self):
      while True:
         if (not qNewsQuery.empty()) and (qNewsQuery.get()):
            logging.debug('Getting News ' + str(qNewsQuery.qsize()) + ' items in queue')
            # get list of company
            for index, region in enumerate (jsonStInfo['Company']):
               self.companyList.insert(index, jsonStInfo['Company'][str(index)])
            for index, company in enumerate (self.companyList):
               for index, source in enumerate (jsonStInfo['News']):
                  recNews = StockM.scrapNews(jsonStInfo['News'][source], company, datetime.datetime.now().strftime("%Y-%m-%d"), jsonStInfo)
                  if not recNews:
                     StockV.noNewsData(source, company)
                  else:
                     result = StockM.newsSentiment(recNews)
                     StockV.showNewsResult(datetime.datetime.now().strftime("%Y-%m-%d"), \
                        source, result)
         else:
            StockV.noNewsService()
            time.sleep(30)
      return

if __name__ == "__main__":
   StockV.startView()

   mDB = StockM.actionsDB() # db object

   p = ProducerThread(name='producer')
   c = ConsumerThread(name='consumer')
   a = AnalyticThread(name='analytic')
   n = NewsThread(name='news')

   p.start()
   c.start()
   a.start()
   n.start()