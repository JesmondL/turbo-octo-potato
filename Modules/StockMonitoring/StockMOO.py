"""pure application logic, which interacts with the database. 
It includes all the information to represent data to the end user.
handling data and business logic"""

# import os
# os.chdir(os.path.dirname(os.path.realpath(__file__)))
import json, os, sqlite3, urllib.request, requests, re, slack, datetime
from bs4 import BeautifulSoup # for html parsing and scraping
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from io import StringIO

MONITOR_SIZE = 25
n_past = 50  # Number of past days want to use to predict/ timesteps
n_future = 2 # Number of days predict into future
n_feature = 1
SIA = SentimentIntensityAnalyzer()

def loadJSON(fp:str):
    try:
        with open(fp) as f:
            jsonObj = json.load(f)
        return jsonObj
    except BaseException as e:
        print (e)
        return None

def create_daily_record(sName:str, sSymbol:str, sDate:str, sTime:str, sValue:str):
    try:
        with open("Daily/"+sSymbol+"_"+sDate+".csv", "a+") as f:
            f.write(sName+","+sSymbol+","+sDate+","+sTime+","+sValue+"\n")
            f.close()
    except BaseException as e:
        print (e)
        return None

def create_closing_record(sSymbol:str, sDate:str, sOpen:str, sClose:str):
    try:
        with open("History/"+sSymbol+"_history.csv", "a+") as f:
            if sDate in f.read():
                print(sSymbol + " data exist")
            else:
                sDelta = float(sOpen)-float(sClose)
                f.write(sDate+","+str(sOpen)+","+str(sClose)+","+str(sDelta)+"\n")
                f.close()
    except BaseException as e:
        print (e)
        return None

def read_daily_record(sSymbol, sDate):
    try:
        rec = pd.read_csv("Daily/"+sSymbol+"_"+sDate+".csv", sep=',',\
            header=None, names = ["Name","Symbol","Date","Time","Value"])
        if len(rec.index) >= n_past:
            return rec
        else:
            return pd.DataFrame()
    except BaseException as e:
        print (e)
        return pd.DataFrame()

def prediction(regressor, inputData, symbol):
    # define scale range
    df = pd.read_csv("History/" + symbol + "_history.csv")
    df = df.Open.to_numpy()
    sc_predict = MinMaxScaler() # normalize data to between 0-1, combo with sigmod
    scale_range = np.array([0, df['Open'].max(axis=1)])
    sc_predict.fit_transform(scale_range.reshape(-1, 1))

    X_inputData = []
    # (1, 50, 1) [rows, timesteps, columns]
    columns = inputData.Value
    columns = columns.tail(n_past)  # get last n_past recent data
    columns = columns.to_numpy()
    # for i in range(0, len(columns)):
    #     X_inputData = columns.tail(n_past)
    #     X_inputData = sc.fit_transform(????) # scale data to between 0-1
    #     X_inputData= X_inputData.reshape(1, n_past, 1)
    #     sc_predict.fit_transform(????) #fit the scale, should be unqiue range per stock
    #     predictions = regressor.predict(X_inputData)
    #     predictions= sc_predict.inverse_transform(predictions)
    
    X_inputData = columns.reshape(1, n_past, 1)
    predictions = regressor.predict(X_inputData)
    inv_predictions = sc_predict.inverse_transform(predictions)
    return predictions, inv_predictions

def newsSentiment(source):
    return SIA.polarity_scores(source)

def findWholeWord(w: str):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

def find_extremes(ticker: object, sDate: str):
    try:
        data = pd.read_csv("Daily/" + ticker.symbol + "_" + sDate + ".csv", sep=',',\
            header=None, names = ["Name","Symbol","Date","Time","Value"])
        ticker.low = data.min(axis = "Value")
        ticker.high = data.max(axis = "Value")
        ticker.delta = ticker.low - ticker.high
    except BaseException as e:
        print (e)

def normalize(min: int, max: int, x: int):
    return (x - min) / (max - min)

def inv_normalize(min: int, max: int, x: int):
    return (max - x) / (max - min)

def SGX(url: str, filename: str, criteria: str, size: str):
# SGX SES 
    yesterday = datetime.date.today().toordinal() - 731760
    r = requests.get(url + yesterday + filename)
    if r.status_code == 200: 
        SGX = StringIO(r.text)
        df = pd.read_csv(SGX, sep=";", index_col=False, header=None, names = ["Date","Name","Remarks","Currency","High","Low","Last","Change","Volume","Bid","Offer","Market","Open","Value","Symbol","Dclose"])
        df.drop(["Remarks","Currency","Last","Bid","Offer","Market","Value","Dclose"], axis=1, inplace=True)
        sort_df = df.sort_values(criteria,ascending=False)
        sort_df.head(size)

class Ticker:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol
        self.scrapeValue = None
        self.newsOutlook = None
        self.analyticResult = None
        self.previousclose = None
        self.open = None
        self.bid = None
        self.ask = None
        self.dayRange = None
        self.weekRange = None
        self.volume = None
        self.avgVolume = None
        self.marketCap = None
        self.beta = None
        self.peRatio = None
        self.eps = None
        self.status = None
        self.high = None
        self.low = None
        self.delta = None

    def scrapWeb(self):
        try:
            page = urllib.request.urlopen('https://sg.finance.yahoo.com/quote/%s?p=%s&.tsrc=fin-srch-v1'%(self.symbol,self.symbol))
            soup = BeautifulSoup(page, "lxml")
            self.previousclose = soup.find("td", attrs={"data-test":"PREV_CLOSE-value"}).text
            self.open = soup.find("td", attrs={"data-test":"OPEN-value"}).text
            self.bid = soup.find("td", attrs={"data-test":"BID-value"}).text
            self.ask = soup.find("td", attrs={"data-test":"ASK-value"}).text
            self.dayRange = soup.find("td", attrs={"data-test":"DAYS_RANGE-value"}).text
            self.weekRange = soup.find("td", attrs={"data-test":"FIFTY_TWO_WK_RANGE-value"}).text
            self.volume = soup.find("td", attrs={"data-test":"TD_VOLUME-value"}).text
            self.avgVolume = soup.find("td", attrs={"data-test":"AVERAGE_VOLUME_3MONTH-value"}).text
            self.marketCap = soup.find("td", attrs={"data-test":"MARKET_CAP-value"}).text
            self.beta = soup.find("td", attrs={"data-test":"BETA_3Y-value"}).text
            self.peRatio = soup.find("td", attrs={"data-test":"PE_RATIO-value"}).text
            self.eps = soup.find("td", attrs={"data-test":"EPS_RATIO-value"}).text
        except BaseException as e:
            print (self.symbol + ' Error')
            self.previousclose = None
            self.open = None
            self.bid = None
            self.ask = None
            self.dayRange = None
            self.weekRange = None
            self.volume = None
            self.avgVolume = None
            self.marketCap = None
            self.beta = None
            self.peRatio = None
            self.eps = None

    def scrapRealTime(self):
        try:
            page = urllib.request.urlopen('https://sg.finance.yahoo.com/quote/%s?p=%s&.tsrc=fin-srch-v1'%(self.symbol,self.symbol))
            soup = BeautifulSoup(page, "lxml")
            self.scrapeValue = soup.body.find('span', attrs={'class':'Trsdu(0.3s) Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(b)'}).text
        except BaseException as e:
            print (self.symbol + ' ' + str(e))
            self.scrapeValue = None

    def scrapNews(self, sSource):
        res = {}
        try:
            if "COMPANY" in sSource:            # business time format
                sSource = sSource.replace('COMPANY', self.name.replace(" ", "%20"))
                # scrap overview page
                page = urllib.request.urlopen(sSource)
                soup = BeautifulSoup(page, "lxml")
                articalList = soup.body.findAll('div', attrs={'class': 'media-body'}) # webpage artical list
                for index, artical in enumerate (articalList):
                    if findWholeWord(self.name)(str(artical)) == None: 
                        continue
                    else:   # webpage artical contains company name
                        url = re.findall("<a href=(.*?)>", str(artical)) # return type list
                        header = artical.find('a').text
                        date = artical.find('time').text
                        body = artical.find('p').text              
                            # scrap artical page
                        page2 = urllib.request.urlopen(url[0][1:-1]) # exclude first and last string ''
                        soup2 = BeautifulSoup(page2, "lxml")
                        articalDetail2 = soup2.body.findAll('div', attrs={'class': 'body-copy'})
                        if len(articalDetail2) == 0:
                            continue
                        else:
                            articalFull2 = re.findall("<p>(.*?)</p>", str(articalDetail2[0]))
                            articalFull2 = ' '.join(articalFull2)
                            res[self.name+"_"+str(index)+"_BT"] = articalFull2
            elif "SYMBOL" in sSource:           # yahoo format
                sSource = sSource.replace('SYMBOL', self.symbol)
                # scrap overview page
                page = urllib.request.urlopen(sSource)
                soup = BeautifulSoup(page, "lxml")
                articalList = soup.body.findAll('div', attrs={'class': 'Ov(h) Pend(14%) Pend(0)--sm1024'}) # webpage artical list
                for index, artical in enumerate (articalList):
                    if findWholeWord(self.name)(str(artical)) == None: 
                        continue
                    else:   # webpage artical header contains company name
                        url = re.findall("<a href=(.*?)>", str(artical))
                        header = artical.find('u').text
                        # date = artical.find('span').text <span data-reactid="???">
                        body = artical.find('p').text
                            # scrap artical page
                        if (len(url) == 0):
                            if (header == ""):
                                continue
                            else:
                                res[self.name+"_"+str(index)+"_YH"] = header
                        else:
                            page2 = urllib.request.urlopen('https://sg.finance.yahoo.com/'+url[0][1:-1])
                            soup2 = BeautifulSoup(page2, "lxml")
                            articalDetail2 = soup2.body.findAll('p', attrs={'class': 'canvas-atom canvas-text Mb(1.0em) Mb(0)--sm Mt(0.8em)--sm'})
                            if len(articalDetail2) == 0:
                                continue
                            else:
                                articalFull2 = re.findall("<p>(.*?)</p>", str(articalDetail2[0]))
                                articalFull2 = ' '.join(articalFull2)
                                res[self.name+"_"+str(index)+"_YH"] = articalFull2
            self.newsOutlook = res
        except BaseException as e:
            print (self.symbol + ' ' + e)

class SendMsg:
    """Constructs the slack message"""

    WELCOME_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "Good day! :wave: \n\n"
            ),
        },
    }

    RETURN_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                ":wave: \n\n"
            ),
        },
    }
    DIVIDER_BLOCK = {"type": "divider"}

    def __init__(self, channel, user):
        self.channel = channel
        self.username = "Service for " + user
        self.icon_emoji = ":wave:"
        self.timestamp = ""
        self.reaction_task_completed = False
        self.pin_task_completed = False

    def init_message_payload(self):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "blocks": [
                self.WELCOME_BLOCK
            ],
        }

    def return_message_payload(self):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "blocks": [
                self.RETURN_BLOCK
            ],
        }

    def trigger_message_payload(self, name, symbol, data, link):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "blocks": [
                *self._get_trigger(name, symbol, data, link)
            ],
        }

    def _get_trigger(self, name, symbol, data, link):
        text = (name + " " + symbol + " " + data)
        information = (
            ":information_source: *<'%s'|"
            "News link>*"%(link)
        )
        return self._get_task_block(text, information)

    def get_payload(self, name, symbol, data):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "blocks": [
                *self._get_block(name, symbol, data)
            ],
        }

    def _get_block(self, name, symbol, data):
        text = (name + " " + symbol + " " + data)
        information = (
            ":information_source: *<'https://sg.finance.yahoo.com/quote/%s?p=%s&.tsrc=fin-srch-v1'|"
            "View on website>*"%(symbol,symbol)
        )
        return self._get_task_block(text, information)

    @staticmethod
    def _get_task_block(text, information):
        return [
            {"type": "section", "text": {"type": "mrkdwn", "text": text}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": information}]},
        ]

class User:
    def __init__(self, name, numOfStocks=20):
        self.name = name
        self.channel = None
        self.choice = None
        self.numMonitor = numOfStocks