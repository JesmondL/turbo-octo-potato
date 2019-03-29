#import os
#os.chdir(os.path.dirname(os.path.realpath(__file__)))
import StockM

def showAllView(db_Read):
   print ('In our db we have %i Tickers' % len(db_Read))

def startView():
   print ('Starting up web monitoring')
   
def endView():
   print ('Goodbye!')