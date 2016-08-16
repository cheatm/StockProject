import pandas
import tushare as ts
import time,os,requests,re
import sqlite3

folder='Data'
DataBase='StockData.db'
dbPath='%s/%s' % (folder,DataBase)

HKindex=['HSI','HSCEI','HSC','HSF','HSCCI','HSP','HSU']
mkt=ts.Market()

def createFolder(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)

def setToken(token):
    ts.set_token(token)
    print(ts.get_token())

def getIndexData(tick):
    print('Requiring index %s' % tick)
    data=mkt.MktIdxd(ticker=tick,field='ticker,tradeDate,openIndex,lowestIndex,highestIndex,closeIndex')

    return(data)

def readIndexData(tick,update=False,f=folder):
    createFolder(f)
    path='%s/%s.xlsx' % (f,tick)
    if os.path.exists(path):

        data=pandas.read_excel(path)

        if update :
            lastDate = data.tradeDate.tolist()[-1]
            ld=time.mktime(time.strptime(lastDate,'%Y-%m-%d'))
            ct=time.localtime()
            ct=time.strftime('%Y-%m-%d',ct)
            ct=time.strptime(ct,'%Y-%m-%d')
            ct=time.mktime(ct)
            if ct>ld:
                data=getIndexData(tick)

            data.to_excel(path)

        return(data)

def getStockData():
    print('Requiring stock data')
    # data=mkt.MktEqud(ticker='600000')
    data=mkt.MktHKEqud(tradeDate='2016-08-10')
    return (data)

def getHKStockData(code,**f):
    url='http://table.finance.yahoo.com/table.csv?s=%s' % code

    param=''
    for k in f.keys():
        param=param+'&%s=%s' % (k,f[k])

    url=url+param+'&ignore=.csv'
    # print(url)
    data=requests.get(url)
    Pattern='(.*?),(.*?),(.*?),(.*?),(.*?),(.*?),(.*?)\n'
    data=re.findall(Pattern,data.text,re.S)
    rData=[]
    for d in data[1:]:
        rData.insert(0,d)

    return(pandas.DataFrame(rData,columns=data[0]))

def saveStockData(name,Data,db=None,con=None):
    close=False

    if con is None:
        con=sqlite3.connect(db)
        close=True

    Data.to_sql(name,con,if_exists='replace')

    if(close):
        con.close()

def readStockData(name,db=None,con=None):
    close=False
    if con is None:
        con=sqlite3.connect(db)
        close=True

    data=pandas.read_sql('''select * FROM "%s"''' % name,con,index_col='index')

    if(close):
        con.close()

    for i in data.index:
        for c in data.columns:
            e=data.get_value(i,c)

            if c != 'Date':

                data.set_value(i,c,float(e))

    return (data)


if __name__ == '__main__':
    # setToken('13a8a6f82ca1f297acfc32c92a6c761b9e00de7ca61a0551fb2d0e62676d76d1')
    code='0700.hk'

    con=sqlite3.connect(dbPath)
    saveStockData(code,getHKStockData(code),con=con)
    data=readStockData(code,con=con)
    con.close()
    print(data)
    # print(getHKStockData('0700.hk'))

