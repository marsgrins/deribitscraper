import urllib.request
import json
from deribit_api import RestClient
from bitex import Gemini
import time
import csv
import os.path
import pandas
from twilio.rest import Client

spy=365*24*60*60
spm=30*24*60*60
spw=7*24*60*60
spd=24*60*60

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
    filename='/home/mstead/deribitscraper/'+name+'.csv'
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
    filename='/home/mstead/deribitscraper/'+name+'.csv'
    if os.path.isfile(filename):
        dbf=dbscrape(name)
        dbi=dbiscrape()
        g=gscrape()
        t1=time.time()
        t2=time.ctime()
        row=[t1,t2,dbf,dbi,g]
        alert(row, name)
        with open(filename,'a',newline='\n') as csvfile:
            filewriter=csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(row)
    else:
        print('error: tried to add to nonexistant file')
def scrapedatum(dbflong):
    name=dbflong['instrumentName']
    filename='/home/mstead/deribitscraper/'+name+'.csv'
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
def loadheader(name):
    with open(name+'.csv') as csvfile:
        raw = list(csv.reader(csvfile, delimiter=',', quotechar='|'))
        header = json.loads(raw[0][0])
    return header
def loaddata(name):
    d = pandas.read_csv(name+'.csv', header=1)
    return d
def age(d):
    n=d.shape[0]-1
    secs=(d.iloc[n]['floattime']-d.iloc[0]['floattime'])
    return secs
def ageindays(d):
    return age(d)/spd
def textme(message='no message'):
    #assumes you have a text file in the same directory called "keys.txt" that has all the relevant stuff in a json-dumped dictionary
    file = open('/home/mstead/deribitscraper/keys.txt', 'r') 
    k=json.loads(file.read())
    account_sid = k['account_sid']
    auth_token = k['auth_token']
    to = k['to']
    from_ = k['from_']
    client = Client(account_sid, auth_token)
    client.messages.create(to=to, from_=from_, body=message)
def alert(row, name):
    delay=spd/4
    if row[4]>row[2]:
        d=loaddata(name)
        if age(d)>delay:
            start=row[0]-delay
            if d[(d.floattime >= start) & (d.deribitlastprice < d.geminilastprice)].shape[0]==0:
                textme('Deribit future '+name+' is trading below Gemini spot price')
if __name__ == "__main__":
    scrapedata()


