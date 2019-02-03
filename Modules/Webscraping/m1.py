import urllib.request
from bs4 import BeautifulSoup # for html parsing and scraping
import json

d = {} # data placeholder
list_tickers = ['Z74.SI']
for ticker in list_tickers:
    page = urllib.request.urlopen('https://sg.finance.yahoo.com/quote/%s?p=%s&.tsrc=fin-srch-v1'%(ticker,ticker))
    soup = BeautifulSoup(page, 'html.parser')
    name_box = soup.find('h1', attrs={'data-reactid':'7'})#title
    left_box = soup.find('div', attrs={'data-test':'left-summary-table'})
    left_box = left_box.find_all('span')
    for c in range (int(len(left_box)/2)):
        d[left_box[c].text] = left_box[c+1].text
    right_box = soup.find('div', attrs={'data-test':'right-summary-table'})
    right_box = right_box.find_all('span')
    for c in range (int(len(right_box)/2)):
        d[right_box[c].text] = right_box[c+1].text
    jd = json.dumps(d)