"""only controller would trigger something in model to be shown in view
handling graphical user interface objects and presentation"""

#import os
#os.chdir(os.path.dirname(os.path.realpath(__file__)))
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from tqdm import tqdm
import StockMOO, requests, json

def slack_webhook_txt(message:str, slack_url:str):
    encoded_data = json.dumps({'text': message}).encode('utf-8')
    response = requests.request("POST", slack_url, data=encoded_data, headers={'Content-Type': 'application/json'})
    print(str(response.status_code))

def slack_webhook_choice(slack_url:str):
    encoded_data = json.dumps({
        "attachments": [
            {
                "fallback": "Stock Information",
                "callback_id": "select_criteria",
                "color": "#36a64f",
                "actions": [
                    {
                        "name": "choice",
                        "text": "Volume",
                        "type": "button",
                        "value": "volume",
                        "confirm": {
                            "title": "Are you sure?",
                            "text": "Confirm?",
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
                            "text": "Confirm?",
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
                            "text": "Confirm?",
                            "ok_text": "Yes",
                            "dismiss_text": "No"
                        }
                    }
                ]
            }
        ]
    }).encode('utf-8')
    response = requests.request("POST", slack_url, data=encoded_data, headers={'Content-Type': 'application/json'})
    print(str(response.status_code))

def startView(slack_url:str):
   print ("Starting up service...")
   slack_webhook_txt("Starting up service...", slack_url)

def selection(slack_url:str):
   slack_webhook_choice(slack_url)

def noService(day:int, hour:int, slack_url:str):
   if day > 4:
      print ("Market does not open on weekends!")
      slack_webhook_txt("Market does not open on weekends!", slack_url)
   elif hour >= 17:
      print ("Market has closed, continue tomorrow!")
      slack_webhook_txt("Market has closed, continue tomorrow!", slack_url)
   elif hour < 9:
      print ("Market has yet to open, wait till 9am!")
      slack_webhook_txt("Market has yet to open, wait till 9am!", slack_url)

def noRealTimeService(slack_url:str):
   print ("No real time scrap service")
   slack_webhook_txt("No real time scrap service", slack_url)

def noRealTimeData(slack_url:str):
   print ("Unable to access information from the website")
   slack_webhook_txt("Unable to access information from the website", slack_url)

def showRealTimeResult(sDate, sTicker, sValue):
   print (sDate + ' ' + sTicker + ' ' + sValue)

def noAnalyticService(slack_url:str):
   print ("No analytic service")
   slack_webhook_txt("No analytic service", slack_url)

def noAnalyticData(name, symbol, slack_url:str):
   print (name + " " + symbol + " data is not ready for analysis")
   slack_webhook_txt(name + " " + symbol + " data is not ready for analysis", slack_url)

def showAnalyticResult(ticker, slack_url:str):
   print (ticker.name + " => " + ticker.analyticResult)
   slack_webhook_txt(ticker.name + " => " + ticker.analyticResult, slack_url)

def noNewsService(slack_url:str):
   print ("No news scrap service")
   slack_webhook_txt("No news scrap service", slack_url)

def noNewsData(sSource:str, name:str, slack_url:str):
   print (sSource + " no news on " + name)
   slack_webhook_txt(sSource + " no news on " + name, slack_url)

def showNewsResult(sDate, sNews, sValue):
   print (sDate + ' ' + sNews + ' Compound : ' + str(sValue['compound']) + \
      ', Neg : ' + str(sValue['neg']) + ', Neu : ' + str(sValue['neu']) + ', Pos : ' + str(sValue['pos']))

def deltaAlert(ticker, slack_url:str):
   print (ticker.name + " " + ticker.symbol + " " + ticker.delta + " exceeds threshold")
   slack_webhook_txt(ticker.name + " " + ticker.symbol + " " + ticker.delta + " exceeds threshold", slack_url)