import urllib.request
import json
from deribit_api import RestClient
from bitex import Gemini
import time
import csv
import os.path

dbclient=RestClient()
gmn= Gemini()

def inssearch(list1,key,value):
    ins2=[]
    for x in range (0,len(list1)):
        if list1[x][key]==value:
            ins2.append(list1[x])
    return ins2
def dbfutureslong(list1):
    ins2=inssearch(list1,'kind','future')
    return ins2
def dbfutures(list1):
    ins2=dbfutureslong(list1)
    ins3=[a['instrumentName'] for a in ins2]
    return ins3
def dbscrape(name):
    dblt=dbclient.getsummary(name)['last']
    return dblt
def dbiscrape():
    return dbclient.index()['btc']
def gscrape():
    return float(gmn.ticker('btcusd').json()['last'])
def createdbcsv(dbflong):
    name=dbflong['instrumentName']
    filename=name+'.csv'
    if os.path.isfile(filename):
        print('error: tried to overwrite data!')
    else:
        with open(filename,'w',newline='\n') as csvfile:
            filewriter=csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow([json.dumps(dbflong)])
            filewriter.writerow(['floattime','localtime','deribitlastprice','deribitindex','geminilastprice'])
def printcsv(name):
    with open(name,newline='') as csvfile:
        reader=csv.reader(csvfile)
        for row in reader:
            print(row)
def addrowcsv(name):
    filename=name+'.csv'
    if os.path.isfile(filename):
        dbf=dbscrape(name)
        dbi=dbiscrape()
        g=gscrape()
        t1=time.time()
        t2=time.ctime()
        with open(filename,'a',newline='\n') as csvfile:
            filewriter=csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow([t1,t2,dbf,dbi,g])
    else:
        print('error: tried to add to nonexistant file')
def scrapedatum(dbflong):
    name=dbflong['instrumentName']
    filename=name+'.csv'
    if not os.path.isfile(filename):
        createdbcsv(dbflong)
    addrowcsv(name)
def scrapedata():
    url="https://www.deribit.com/api/v1/public/getinstruments"
    webURL= urllib.request.urlopen(url)
    data=webURL.read()
    encoding = webURL.info().get_content_charset('utf-8')
    instruments = json.loads(data.decode(encoding))
    ins = instruments.get("result")
    dbfslong=dbfutureslong(ins)
    n=len(dbfslong)
    for i in range(0,n):
        scrapedatum(dbfutureslong(ins)[i])
if __name__ == "__main__":
    scrapedata()


