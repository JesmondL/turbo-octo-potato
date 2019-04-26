"""only controller would trigger something in model to be shown in view
handling graphical user interface objects and presentation"""

#import os
#os.chdir(os.path.dirname(os.path.realpath(__file__)))
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from tqdm import tqdm
import StockM

def startView():
   print ('Starting up monitoring program...')

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

def noAnalyticData(jsonStInfo, ticker):
   print (jsonStInfo['Singapore_Stock'][ticker] + " data is not ready")

def showAnalyticResult(result):
   print (result)

def noNewsService():
   print ("No news scrap service")

def noNewsData(sSource, sCompany):
   print (sSource + " no news on " + sCompany)

def showNewsResult(sDate, sNews, sValue):
   print (sDate + ' ' + sNews + ' ' + sValue)
