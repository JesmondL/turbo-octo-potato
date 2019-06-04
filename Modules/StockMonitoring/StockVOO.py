"""only controller would trigger something in model to be shown in view
handling graphical user interface objects and presentation"""

#import os
#os.chdir(os.path.dirname(os.path.realpath(__file__)))
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from tqdm import tqdm
import StockMOO

def startView():
   print ("Starting up service...")

def noService(day, hour):
   if day > 4:
      print ("Market does not open on weekends!")
   elif hour >= 17:
      print ('Market has closed, continue tomorrow!')
   elif hour < 9:
      print ('Market has yet to open, wait till 9am!')

def noRealTimeService():
   print ("No real time scrap service")

def noRealTimeData():
   print ("Unable to access information from the website")

def showRealTimeResult(sDate, sTicker, sValue):
   print (sDate + ' ' + sTicker + ' ' + sValue)

def noAnalyticService():
   print ("No analytic service")

def noAnalyticData(name, symbol):
   print (name + " " + symbol + " data is not ready for analysis")

def showAnalyticResult(ticker):
   print (ticker.name + " => " + ticker.analyticResult)

def noNewsService():
   print ("No news scrap service")

def noNewsData(sSource, name):
   print (sSource + " no news on " + name)

def showNewsResult(sDate, sNews, sValue):
   print (sDate + ' ' + sNews + ' Compound : ' + str(sValue['compound']) + \
      ', Neg : ' + str(sValue['neg']) + ', Neu : ' + str(sValue['neu']) + ', Pos : ' + str(sValue['pos']))

def deltaAlert(ticker):
   print (ticker.name + " " + ticker.symbol + " " + ticker.delta + " exceeds threshold")