import pandas
import tushare as ts
import time,os,requests,re
import sqlite3,random

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
    '''

    :param code: stockCode (0700.hk, 600000.ss .....)
    :param f:
        a = begin month - 1
        b = begin day
        c = begin year
        d = end month - 1
        e = end day
        f = end year
        g = timeframe(w:week, d:day, w:week, m:month)
    :return: DataFrame()
    '''

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

    out=pandas.DataFrame(rData,columns=data[0])
    for i in out.index:
        for c in data[0][1:]:
            v=out.get_value(i,c)

            out.set_value(i,c,float(v))

    out.set_index('Date',inplace=True)
    Time=[]
    for i in out.index:
        Time.append(
            time.mktime(
                time.strptime(i,'%Y-%m-%d')
            )
        )
    out.insert(0,'time',Time)

    return(out)

def saveStockData(name,Data,db=None,con=None,if_exists='replace'):
    '''

    :param name: name of data
    :param Data: data to be saved
    :param db: database address
    :param con: connected database object
            There must be a db or a con
    :param if_exists: {'fail', 'replace', 'append'}
            - fail: If table exists, do nothing.
            - replace: If table exists, drop it, recreate it, and insert data.
            - append: If table exists, insert data. Create if does not exist.
    :return:
    '''

    close=False

    if con is None:
        con=sqlite3.connect(db)
        close=True

    Data.to_sql(name,con,if_exists=if_exists)

    if(close):
        con.close()


def readStockData(name,db=None,con=None):
    '''

    :param name: table name in the database
    :param db: database path
    :param con: connected database object
        There must be a db or a con
    :return:
    '''

    close=False
    if con is None:
        con=sqlite3.connect(db)
        close=True

    data=pandas.read_sql('''select * FROM "%s"''' % name,con,index_col='index')

    if(close):
        con.close()

    # for i in data.index:
    #     for c in data.columns:
    #         e=data.get_value(i,c)
    #
    #         if c != 'Date':
    #
    #             data.set_value(i,c,float(e))

    return (data)


def saveHKOption(db=dbPath):
    path='%s/%s' % (folder,'HK Option.xlsx')
    table=pandas.read_excel(path,'Sheet1')

    con=sqlite3.connect(dbPath)

    for i in table['IB Symbol']:
        if type(i)==type(0):
            code=str(i)
            while(len(code)<4):
                code='%s%s' % (0,code)
            code=code+'.hk'

            print('collecting %s ' % code)
            try:
                saveStockData(code,getHKStockData(code),con=con)
            except Exception as e:
                print(e)

            time.sleep(random.random()*2)
    con.close()

def changeDBdata(table,db=None,con=None):
    close=False
    if con==None:

        con=sqlite3.connect(db)
        close=True



    data=pandas.read_sql('''select * FROM "%s"''' % table,con,index_col='Date')
    print(table)
    print(data)
    # Time=[]
    # for d in data.index:
    #     Time.append(time.mktime(time.strptime(d,'%Y-%m-%d')))
    #
    #
    # data.insert(0,'time',Time)
    # data.drop(['index'],axis=1,inplace=True)
    # data.to_sql(table,con,if_exists='replace')

    # print(data)
    if close:
        con.close()

def updateStockData(code,db=None,con=None):
    close=False
    if con==None:

        con=sqlite3.connect(db)
        close=True

    # data=data=pandas.read_sql('''select * FROM "%s"''' % code,con)
    last=con.execute('''SELECT * FROM "%s" ORDER BY rowid DESC ''' % code).fetchone()
    today=time.strftime('%Y-%m-%d',time.localtime())

    if today==last[0]:
        return (0)

    lastdate=last[0].split('-')
    try:
        update=getHKStockData(code,a=int(lastdate[1])-1,b=int(lastdate[2])+1,c=int(lastdate[0]))
        update.to_sql(code,con,if_exists='append')
        print(pandas.read_sql('select * from "%s"' % code,con))
    except Exception as e:
        print(e)

    if close:
        con.close()


if __name__ == '__main__':
    # setToken('13a8a6f82ca1f297acfc32c92a6c761b9e00de7ca61a0551fb2d0e62676d76d1')
    code='0001.hk'

    con=sqlite3.connect(dbPath)
    table_names=con.execute('''select name from sqlite_master where type='table' ''').fetchall()

    # updateStockData(table_names[0][0],con=con)
    # changeDBdata(table_names[0][0],con=con)

    con.close()


    # saveHKOption()

