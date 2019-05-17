"""triggers something in model to show in view
handling the user interface and application"""

#CTL+SHIFT+P python interpretor to webscraping
#pip install required package
# https://sg.finance.yahoo.com/quote/Z74.SI/history?period1=1262275200&period2=1546358400&interval=1d&filter=history&frequency=1d

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
import StockMOO, StockVOO
import time, json, requests, datetime, threading, queue, logging, copy, slack, certifi
from keras.models import load_model
import pandas as pd
import ssl as ssl_lib

BUF_SIZE = 1
qWebQuery = queue.Queue(BUF_SIZE)
qAnalyticQuery = queue.Queue(BUF_SIZE)
qNewsQuery = queue.Queue(BUF_SIZE)
jsonStInfo = StockMOO.loadJSON('stock_infoOO.json')
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)
tickers = []
user_id = []

class ProducerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
    args=(), kwargs=None, verbose=None):
        super(ProducerThread,self).__init__()
        self.target = target
        self.name = name
        self.cnt = 120

    def run(self):
        while True:
            if not qNewsQuery.full():
                if self.cnt == 120: # 120*120=14400secs = 4hrs
                    qNewsQuery.put(True)
                    logging.debug('Putting News Query : ' + str(qNewsQuery.qsize()) + ' items in queues')
                    self.cnt = 1
                else:
                    self.cnt = self.cnt + 1
            if not qWebQuery.full():
                if (int(datetime.datetime.now().hour) >= int(jsonStInfo['Singapore_Time']['open'])) & \
                (int(datetime.datetime.now().hour) < int(jsonStInfo['Singapore_Time']['close'])) & \
                (datetime.datetime.now().weekday() <= 5): # within operating hour and weekdays will proceed
                    qWebQuery.put(True)
                    qAnalyticQuery.put(True)
                else:
                    StockVOO.noService(datetime.datetime.now().weekday(), datetime.datetime.now().hour)
                    qWebQuery.put(False)
                    qAnalyticQuery.put(False)
                    logging.debug('Putting Web Analytic Query : ' + str(qWebQuery.qsize()) + ' items in queues')
            time.sleep(120)
        return

class ScrapeThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
    args=(), kwargs=None, verbose=None):
        super(ScrapeThread,self).__init__()
        self.target = target
        self.name = name
        return

    def run(self):
        while True:
            if not qWebQuery.empty():
                status = qWebQuery.get()
                logging.debug('Getting RealTime Data : ' + str(qWebQuery.qsize()) + ' items in queue')
                if status:  # market operational
                    for ticker in tickers:
                        ticker.scrapRealTime() 
                        if ticker.scrapeValue == None:
                            StockVOO.noRealTimeData()
                        else:
                            StockMOO.create_daily_record(ticker.name,\
                                ticker.symbol, \
                                datetime.datetime.now().strftime("%Y-%m-%d"), \
                                datetime.datetime.now().strftime("%H:%M"), \
                                ticker.scrapeValue)
                        time.sleep(5)
                else:       # market non operational
                    for ticker in tickers:
                        ticker.scrapWeb()
                        ticker.scrapRealTime()
                        if (ticker.scrapeValue == None) or (ticker.previousclose == None):
                            StockVOO.noRealTimeData()
                        else:
                            StockMOO.create_closing_record(ticker.symbol,\
                                datetime.datetime.now().strftime("%Y-%m-%d"), \
                                    ticker.open, ticker.scrapeValue)
                            time.sleep(5)
                    StockVOO.noRealTimeService()
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
                    for ticker in tickers:
                        rec = StockMOO.read_daily_record(ticker.symbol, \
                            datetime.datetime.now().strftime("%Y-%m-%d"))
                        if rec.empty:
                            StockVOO.noAnalyticData(ticker.name, ticker.symbol)
                        else:
                            result = StockMOO.prediction(rnn, rec)
                            StockVOO.showAnalyticResult(ticker.name, result)
                            StockMOO.find_daily_extremes(ticker.symbol, \
                                datetime.datetime.now().strftime("%Y-%m-%d"), rec)
                else:
                    StockVOO.noAnalyticService()
        return

class NewsThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
    args=(), kwargs=None, verbose=None):
        super(NewsThread,self).__init__()
        self.target = target
        self.name = name
        return

    def run(self):
        while True:
            if (not qNewsQuery.empty()) and (qNewsQuery.get()):
                logging.debug('Getting News ' + str(qNewsQuery.qsize()) + ' items in queue')
                for ticker in tickers:
                    for source in jsonStInfo['News']:
                        ticker.scrapNews(jsonStInfo['News'][source])
                        if ticker.newsOutlook == None:
                            StockVOO.noNewsData(source, ticker.name)
                        else:
                            for key, value in ticker.newsOutlook.items():
                                result = StockMOO.newsSentiment(value)
                                StockVOO.showNewsResult(datetime.datetime.now().strftime("%Y-%m-%d"), key, result)
            else:
                StockVOO.noNewsService()
                time.sleep(3600)
        return

# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link the message callback to the 'message' event.
@slack.RTMClient.run_on(event="message")
def message(**payload):
    """
    Trigger flow when specific text is detected
    """
    data = payload["data"]
    web_client = payload["web_client"]
    channel_id = data.get("channel")
    if data.get("user") in user_id:
        print ("User is in the system")
    else:
        user_id.append(data.get("user"))
        StockMOO.start_session(web_client, data.get("user"), channel_id, data.get("text"), jsonStInfo)

def initialize():
    for t in jsonStInfo['Symbol']:
        tickers.append(StockMOO.Ticker(jsonStInfo['Company'][t], jsonStInfo['Symbol'][t]))

if __name__ == "__main__":
    StockVOO.startView()

    initialize() # init tickers obj into a list

    p = ProducerThread(name='producer')
    s = ScrapeThread(name='scrape')
    a = AnalyticThread(name='analytic')
    n = NewsThread(name='news')

    p.start()
    s.start()
    a.start()
    n.start()

    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    slack_token = os.environ["SLACK_BOT_TOKEN"] # stockservice app API token
    rtm_client = slack.RTMClient(token=slack_token, ssl=ssl_context)
    rtm_client.start()