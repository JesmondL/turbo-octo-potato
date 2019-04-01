"""only controller would trigger something in model to be shown in view
handling graphical user interface objects and presentation"""

#import os
#os.chdir(os.path.dirname(os.path.realpath(__file__)))
import StockM

def showAllView(db_Read):
   print ('In our db we have %i Tickers' % len(db_Read))

def startView():
   print ('Starting up monitoring program...')
   
def scrappedView(ticker):
   print ('Scrapped ' + ticker + ' information')

def endView(day, hour):
   if day > 4:
      print ("Market does not open on weekends!")
   elif hour >= 17:
      print ('Market has closed, continue tomorrow!')
   elif hour < 9:
      print ('Market has yet to open, wait till 9am!')