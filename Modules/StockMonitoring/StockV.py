#import os
#os.chdir(os.path.dirname(os.path.realpath(__file__)))
import StockM

def showAllView(db_Read):
   print ('In our db we have %i Tickers. Here they are:' % len(db_Read))
   for item in db_Read:
      print (item)

def startView():
   print ('Starting up web monitoring')
   print ('Loading list of stock to be monitor')
   
def endView():
   print ('Goodbye!')