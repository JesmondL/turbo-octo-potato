"""triggers something in model to show in view
handling the user interface and application"""

#CTL+SHIFT+P python interpretor to webscraping
#pip install required package
# https://sg.finance.yahoo.com/quote/Z74.SI/history?period1=1262275200&period2=1546358400&interval=1d&filter=history&frequency=1d
# https://github.com/slackapi/WeAreDevs/blob/master/complete-example.py

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
import StockMOO, StockVOO
import time, json, requests, datetime, threading, queue, logging, copy, certifi
from keras.models import load_model
from slack import WebClient, RTMClient 
import pandas as pd
import ssl as ssl_lib

BUF_SIZE = 1
qWebQuery = queue.Queue(BUF_SIZE)
qAnalyticQuery = queue.Queue(BUF_SIZE)
qNewsQuery = queue.Queue(BUF_SIZE)
jsonStInfo = StockMOO.loadJSON('stock_infoOO.json')
config = StockMOO.loadJSON('config.json')
logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)
tickers = []
users = [] # user tracking
DELTA_THRESHOLD = 0.01
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"] # stockservice app's bot API token
slack_WC = WebClient(token=SLACK_BOT_TOKEN)
SLACK_WH = os.environ["SLACK_WEBHOOK"]
userRequested = False # request for analytic service

class ProducerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
    args=(), kwargs=None, verbose=None):
        super(ProducerThread,self).__init__()
        self.target = target
        self.name = name
        self.cnt = 120
        self.stopped = False

    def run(self):
        while True:
            if not qNewsQuery.full():
                if self.cnt == 120: # 120*120=4hrs interval
                    qNewsQuery.put(True)
                    logging.debug('Putting News Query : ' + str(qNewsQuery.qsize()) + ' items in queues')
                    self.cnt = 1 # reset count
                else:
                    self.cnt = self.cnt + 1
            if not qWebQuery.full():
                if (int(datetime.datetime.now().hour) >= int(jsonStInfo['Singapore_Time']['open'])) & \
                (int(datetime.datetime.now().hour) < int(jsonStInfo['Singapore_Time']['close'])) & \
                (datetime.datetime.now().weekday() <= 5): # within operating hour and weekdays will proceed
                    qWebQuery.put(True)
                    qAnalyticQuery.put(True)
                    self.stopped = False
                elif (int(datetime.datetime.now().hour) < int(jsonStInfo['Singapore_Time']['open'])) & \
                (int(datetime.datetime.now().hour) > int(jsonStInfo['Singapore_Time']['close'])) & \
                (datetime.datetime.now().weekday() > 5) & self.stopped == False: # notifty 1st off market
                    StockVOO.noService(datetime.datetime.now().weekday(), datetime.datetime.now().hour, SLACK_WH)
                    qWebQuery.put(False)
                    qAnalyticQuery.put(False)
                    self.stopped = True
                logging.debug('Putting Web Analytic Query : ' + str(qWebQuery.qsize()) + ' items in queues')
            time.sleep(120) # 2mins break
        return

class ScrapeThread(threading.Thread):
    """continuously getting data from web"""
    def __init__(self, group=None, target=None, name=None,
    args=(), kwargs=None, verbose=None):
        super(ScrapeThread,self).__init__()
        self.target = target
        self.name = name
        self.stopped = False  # flag to stop no scrapping feed
        return

    def run(self):
        while True:
            if not qWebQuery.empty():
                status = qWebQuery.get()
                logging.debug('Getting RealTime Data : ' + str(qWebQuery.qsize()) + ' items in queue')
                if status: # market operational
                    for ticker in tickers:
                        ticker.scrapRealTime() 
                        if ticker.scrapeValue == None:
                            StockVOO.noRealTimeData(SLACK_WH) # temporary no scrapping
                        else:
                            StockMOO.create_daily_record(ticker.name,\
                                ticker.symbol, \
                                datetime.datetime.now().strftime("%Y-%m-%d"), \
                                datetime.datetime.now().strftime("%H:%M"), \
                                ticker.scrapeValue)
                        time.sleep(5)
                    self.stopped = False
                elif (status == False) and (self.stopped == False): # notify on 1st market off
                    for ticker in tickers:
                        ticker.scrapWeb()
                        ticker.scrapRealTime()
                        if (ticker.scrapeValue == None) or (ticker.previousclose == None):
                            StockVOO.noRealTimeData(SLACK_WH) # temporary no scrapping
                        else:
                            StockMOO.create_closing_record(ticker.symbol,\
                                datetime.datetime.now().strftime("%Y-%m-%d"), \
                                    ticker.open, ticker.scrapeValue)
                            time.sleep(5)
                    # SGX SES 
                    StockMOO.SGX(config['SES_URL'], config['SGX_HIS_FILE'], "Volume", "25")
                    StockVOO.noRealTimeService(SLACK_WH) # temporary no scrapping
                    self.stopped = True
        return

class AnalyticThread(threading.Thread):
    """analyse per user request"""
    def __init__(self, group=None, target=None, name=None,
    args=(), kwargs=None, verbose=None):
        super(AnalyticThread,self).__init__()
        self.target = target
        self.name = name
        self.stopped = False  # flag to stop no analytic feed
        return

    def run(self):
        rnn = load_model('model.h5')
        while True:
            if not qAnalyticQuery.empty():
                status = qAnalyticQuery.get()
                logging.debug('Getting Analysis Trend : ' + str(qAnalyticQuery.qsize()) + ' items in queue')
                if status and userRequested:
                    for ticker in tickers:
                        rec = StockMOO.read_daily_record(ticker.symbol, \
                            datetime.datetime.now().strftime("%Y-%m-%d"))
                        if rec.empty:
                            StockVOO.noAnalyticData(ticker.name, ticker.symbol, SLACK_WH) # temporary no analytic
                        else:
                            ticker.analyticResult = StockMOO.prediction(rnn, rec, ticker.symbol)
                            StockVOO.showAnalyticResult(ticker, SLACK_WH)
                            StockMOO.find_extremes(ticker.symbol, datetime.datetime.now().strftime("%Y-%m-%d"))
                            if (ticker.delta/ticker.high) >= DELTA_THRESHOLD: # difference greater than threshold
                                StockVOO.deltaAlert(ticker, SLACK_WH)
                    self.stopped = False
                elif (status == False) and (self.stopped == False) and userRequested: # notify on 1st market off
                    StockVOO.noAnalyticService(SLACK_WH)
                    self.stopped = True
        return

class NewsThread(threading.Thread):
    """large intervals getting data from web"""
    def __init__(self, group=None, target=None, name=None,
    args=(), kwargs=None, verbose=None):
        super(NewsThread,self).__init__()
        self.target = target
        self.name = name
        self.stopped = False # flag to stop spam not available feed
        return

    def run(self):
        while True:
            if (not qNewsQuery.empty()) and (qNewsQuery.get()): # consume the queue
                logging.debug('Getting News ' + str(qNewsQuery.qsize()) + ' items in queue')
                for ticker in tickers:
                    for source in jsonStInfo['News']:
                        ticker.scrapNews(jsonStInfo['News'][source])
                        if ticker.newsOutlook == None:
                            StockVOO.noNewsData(source, ticker.name, SLACK_WH)
                        else:
                            for key, value in ticker.newsOutlook.items():
                                result = StockMOO.newsSentiment(value)
                                StockVOO.showNewsResult(datetime.datetime.now().strftime("%Y-%m-%d"), key, result)
                self.stopped = False
            elif self.stopped == False: # notify on 1st market off
                StockVOO.noNewsService(SLACK_WH)
                self.stopped = True
            else:                       # stop notify subsequent market off
                self.stopped = True
        return

# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link the message callback to the 'message' event.
@RTMClient.run_on(event="message")
def message(**payload):
    """
    Trigger flow when user entered text is detected
    """
    data = payload["data"]
    if data.get("user") != None:        # ignore msg event by script input
        session = StockMOO.SendMsg(data.get("channel"), data.get("user"))
        if data.get("user") in users:   # returned user
            pass
        else:                           # new user
            users.append(data.get("user"))
            # Get the init message payload
            message = session.init_message_payload()
            # Post the init message in Slack
            slack_WC.chat_postMessage(**message)

        if data.get("text") == "a":
            StockVOO.selection(SLACK_WH)
        elif data.get("text") == "b":
            userRequested = True # request analytic service
        else:
            # Text processing
            for ticker in tickers:
                if data.get("text") == ticker:
                    if ticker.symbol[:3].lower() in data.get("text").lower(): # take first 3 char compare, eg Z74
                        message = session.get_payload(ticker.name, ticker.symbol, ticker.scrapeValue)
                        break
                    if ticker.name.lower() in data.get("text").lower():
                        message = session.get_payload(ticker.name, ticker.symbol, ticker.scrapeValue)
                        break
                    # Post message in Slack
                    slack_WC.chat_postMessage(**message)
                    break

def slack_webhook_txt(message:str):
    encoded_data = json.dumps({'text': message}).encode('utf-8')
    response = requests.request("POST", SLACK_WH, data=encoded_data, headers={'Content-Type': 'application/json'})
    print(str(response.status_code))

def slack_webhook_data(ticker):   
    encoded_data = json.dumps({
        "attachments": [
            {
                "fallback": "Stock Information",
                "color": "#36a64f",
                "fields": [
                    {
                        "title": "Company",
                        "value": ticker.name
                    },
                    {
                        "title": "Symbol",
                        "value": ticker.symbol
                    },
                    {
                        "title": "Value",
                        "value": ticker.scrapeValue
                    }
                ]
            }
        ]
    }).encode('utf-8')
    response = requests.request("POST", SLACK_WH, data=encoded_data, headers={'Content-Type': 'application/json'})
    print(str(response.status_code))

def slack_webhook_choice():
    encoded_data = json.dumps({
        "attachments": [
            {
                "fallback": "Stock Information",
                "color": "#36a64f",
                "actions": [
                    {
                        "name": "choice",
                        "text": "Volume",
                        "type": "button",
                        "value": "volume",
                        "confirm": {
                            "title": "Are you sure?",
                            "text": "Comfirm?",
                            "ok_text": "Yes",
                            "dismiss_text": "No"
                        }
                    },
                    {
                        "name": "choice",
                        "text": "Gain",
                        "style": "primary",
                        "type": "button",
                        "value": "gain",
                        "confirm": {
                            "title": "Are you sure?",
                            "text": "Comfirm?",
                            "ok_text": "Yes",
                            "dismiss_text": "No"
                        }
                    },
                    {
                        "name": "choice",
                        "text": "Loss",
                        "style": "danger",
                        "type": "button",
                        "value": "loss",
                        "confirm": {
                            "title": "Are you sure?",
                            "text": "Comfirm?",
                            "ok_text": "Yes",
                            "dismiss_text": "No"
                        }
                    }
                ]
            }
        ]
    }).encode('utf-8')
    response = requests.request("POST", SLACK_WH, data=encoded_data, headers={'Content-Type': 'application/json'})
    print(str(response.status_code))

def slack_api_choice(channel):
    CHOICE_BLOCK = [
            {
            "blocks": [
                {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Volume"
                        },
                        "style": "primary",
                        "value": "volume"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Gain"
                        },
                        "style": "primary",
                        "value": "gain"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Loss"
                        },
                        "style": "primary",
                        "value": "loss"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Delta"
                        },
                        "style": "primary",
                        "value": "delta"
                    }
                ]
            }
        ]
        }
    ]
    slack_WC.api_call("chat.postMessage", json={"channel":channel,"text":"Which criteria would you like to sort on? :coffee:", "attachments":CHOICE_BLOCK})

def std_initialize():
    for t in jsonStInfo['Symbol']:
        tickers.append(StockMOO.Ticker(jsonStInfo['Company'][t], jsonStInfo['Symbol'][t]))

def cust_initialize():
    for t in jsonStInfo['Symbol']:
        tickers.append(StockMOO.Ticker(jsonStInfo['Company'][t], jsonStInfo['Symbol'][t]))

if __name__ == "__main__":
    StockVOO.startView(SLACK_WH)
    
    std_initialize() # init fixed tickers obj list
    # cust_initialize() # init filtered tickers obj list

    p = ProducerThread(name='producer')
    s = ScrapeThread(name='scrape')
    a = AnalyticThread(name='analytic')
    n = NewsThread(name='news')

    # p.start()
    # s.start()
    # a.start()
    # n.start()

    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    rtm_client = RTMClient(token=SLACK_BOT_TOKEN, ssl=ssl_context)
    rtm_client.start()