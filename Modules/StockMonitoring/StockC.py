"""triggers something in model to show in view
handling the user interface and application"""

#CTL+SHIFT+P python interpretor to webscraping
#pip install required package
# https://sg.finance.yahoo.com/quote/Z74.SI/history?period1=1262275200&period2=1546358400&interval=1d&filter=history&frequency=1d

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
import StockM, StockV
import time, json, requests, datetime, threading, queue, logging

BUF_SIZE = 10
qWebQuery = queue.Queue(1)
qAnalyticQuery = queue.Queue(BUF_SIZE)
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

   def run(self):
      while True:
         if not qWebQuery.full():
            if (int(datetime.datetime.now().hour) >= int(jsonStInfo['Singapore_Time']['open'])) & \
               (int(datetime.datetime.now().hour) < int(jsonStInfo['Singapore_Time']['close'])) & \
               (datetime.datetime.now().weekday() <= 5): # within operating hour and weekdays will proceed
               gOperating = True
            else:
               gOperating = False
            qWebQuery.put(gOperating)
            logging.debug('Putting ' + str(gOperating)  
                              + ' : ' + str(qWebQuery.qsize()) + ' items in queue')
            time.sleep(10)
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
            logging.debug('Getting ' + str(status) 
                              + ' : ' + str(qWebQuery.qsize()) + ' items in queue')
            if status:
               for ticker in jsonStInfo['Singapore_Stock']:
                  value = StockM.scrapRealTime(jsonStInfo['Singapore_Stock'][ticker], jsonStInfo, 'yahoo') # get realtime value
                  if value == None:
                     continue
                  else:
                     StockV.scrappedView(datetime.datetime.now().strftime("%H:%M"), ticker, value)
                     #name, symbol, date, time, value
                     StockM.create_daily_record(ticker,\
                        jsonStInfo['Singapore_Stock'][ticker], \
                        datetime.datetime.now().strftime("%Y-%m-%d"), \
                        datetime.datetime.now().strftime("%H:%M"), \
                        value)
                  time.sleep(5)
            else:
               for ticker in jsonStInfo['Singapore_Stock']:
                  scraps = StockM.scrapWeb(jsonStInfo['Singapore_Stock'][ticker], jsonYmap)
                  value = StockM.scrapRealTime(jsonStInfo['Singapore_Stock'][ticker], jsonStInfo, 'yahoo')
                  if (scraps == None) or (value == None):
                     continue
                  else:
                     # Date, Open, Close
                     StockM.create_closing_record(jsonStInfo['Singapore_Stock'][ticker],\
                        datetime.datetime.now().strftime("%Y-%m-%d"), scraps['Open'], value)
                     time.sleep(5)
      return

class AnalyticThread(threading.Thread):
   def __init__(self, group=None, target=None, name=None,
   args=(), kwargs=None, verbose=None):
      super(ConsumerThread,self).__init__()
      self.target = target
      self.name = name
      return

   def run(self):
      while True:
         if not q.empty():
            status = q.get()
      return

if __name__ == "__main__":
   StockV.startView()

   mDB = StockM.actionsDB() # db object

   p = ProducerThread(name='producer')
   c = ConsumerThread(name='consumer')
   
   p.start()
   c.start()