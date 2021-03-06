import pandas
import tushare as ts
import time,os,requests,re
import sqlite3,random
import threadpool


folder='Data'
folder2='E:/FinanceData/Data'


savePath=open('ini/StockSavePath.txt').read()

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
    data.pop('ticker')
    t=[]
    for i in data['tradeDate']:
        t.append(time.mktime(time.strptime(i,'%Y-%m-%d')))
    data.insert(1,'time',t)

    return(data.set_index('time'))

def readIndexData(tick,update=False,f=savePath):
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

    print(code,f)

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

def saveStockData(table,Data,db=None,con=None,if_exists='replace'):
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

    Data.to_sql(table,con,if_exists=if_exists)

    if(close):
        con.close()


def readStockData(table,code=None,db=None,con=None):
    '''

    :param name: table name in the database
    :param db: database path
    :param con: connected database object
        There must be a db or a con
    :return:
    '''

    if db is None:
        db='%s/%s.db' % (savePath,code)

    print(db)
    close=False
    if con is None:
        con=sqlite3.connect(db)
        close=True

    data=pandas.read_sql('''select * FROM %s''' % table,con)

    if(close):
        con.close()

    return (data)

def read_sql(table,code=None,dbpath=None,con=None):
    close=False

    if dbpath is None:
        dbpath='%s/%s.db' % (savePath,code)

    if con is None:
        con = sqlite3.connect(dbpath)
        close=True

    data=pandas.read_sql('''select * FROM %s''' % table,con)

    if close:
        con.close()

    return data

def updateIndex(name='HKindex.db',pathFolder=savePath,index=HKindex):
    con=sqlite3.connect("%s/%s" % (pathFolder,name))
    for i in index:
        data=getIndexData(i)
        data.to_sql(i,con,if_exists='replace')
        print(i)
    con.close()

def changeDBdata(table,db=None,con=None):
    close=False
    if con==None:

        con=sqlite3.connect(db)
        close=True



    data=pandas.read_sql('''select * FROM "%s"''' % table,con,index_col='Date')
    path='%s/%s.db' % (folder,table)
    newdb=sqlite3.connect(path)
    data.to_sql('Day',newdb,if_exists='replace')
    print(path)

    if close:
        con.close()

def updateAllStock(pathFolder=savePath):
    table_names=open('ini/HKStockList.txt').read().split(',')

    for name in table_names:

        path='%s/%s.db' % (pathFolder,name)
        print(path)
        con=sqlite3.connect(path)
        updateStockData(code=name,con=con)
        con.close()

def updateStockData(code,table='Day',db=None,con=None):
    '''

    :param code:
    :param table:
    :param con:
    :return:
    '''

    if db is None:
        db='%s/%s.db' % (savePath,code)

    close=False
    if con==None:

        con=sqlite3.connect(db)
        close=True

    last=con.execute('''SELECT * FROM "%s" ORDER BY rowid DESC ''' % table).fetchone()
    today=time.strftime('%Y-%m-%d',time.localtime())

    if today==last[0]:
        print('already updated')
        return (0)

    lastdate=last[1].split('-')
    print(lastdate)
    try:

        update=getHKStockData(code,a=int(lastdate[1])-1,b=int(lastdate[2])+1,c=int(lastdate[0]))
        print(update)

        # print(pandas.read_sql('select * from "%s"' % code,con))
    except Exception as e:
        print('error:',e)
        return 0

    update.to_sql(table,con,if_exists='append')

    if close:
        con.close()

def getBasicData(name,type=0):
    '''

    :param name:
    :param type:
        0:'financial-summary'
        1:'income-statement'
        2:'balance-sheet'
        3:'cash-flow'
    :return:
    '''

    sheetType=[
        'financial-summary','income-statement','balance-sheet','cash-flow'
    ]

    url='http://www.investing.com%s-%s' % (name,sheetType[type])
    header=[
        {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36 OPR/39.0.2256.48'},
        {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586'},
        {'user-agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36'}
    ]

    page=requests.get(url,headers=header[random.randint(0,2)])

    if type>0:
        # 报表
        tablePattern='''<div id="rrtable">(.*?)<div class="arial'''
        table=re.findall(tablePattern,page.text,re.S)

        timePattern='''<th>.*?<span class="bold">(.*?)</span>.*?<div class=.*?>(.*?)</div>'''
        Time=re.findall(timePattern,table[0],re.S)
        for t in range(0,len(Time)):
            Time[t]='%s/%s' % (Time[t][0],Time[t][1])
        Time.insert(0,'label')

        dataPattern='''<tr class.*?>.*?<td>.*?<span class.*?>(.*?)<.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>'''
        data=re.findall(dataPattern,table[0],re.S)

        out=pandas.DataFrame(data,columns=Time)
        out.set_index('label',inplace=True)

        time.sleep(random.random()*3)
        return (out)

    else:
        # Summary
        pattern='''<div class="infoLine">.*?<span class="float_lang.*?">(.*?)</span>.*?<span class="float_lang.*?">(.*?)</span>'''
        summary=re.findall(pattern,page.text,re.S)

        month=time.strftime("%Y/%m",time.localtime())
        summary=pandas.DataFrame(summary,columns=['time',month])
        summary.set_index('time',inplace=True)
        for i in summary.index:
            value=summary.get_value(i,month)
            try:
                if '%' in value:
                    n=value.split('%')
                    summary.set_value(i,month,float(n[0])/100)
                else:
                    if '-' not in value:
                        summary.set_value(i,month,float(value))
            except Exception as e:
                print(e)

        time.sleep(random.randint(0,2)+random.random())
        return (summary.T)

def saveHKBasic(data,db=None,con=None):

    close=False
    if con==None:

        con=sqlite3.connect(db)
        close=True

    data.to_sql('basic',con,if_exists='replace')
    print(data)

    if close:
        con.close()


def getInvestingStockAddress(text):

    pattern='''<td data-column-name="name_trans".*?href="(.*?)".*?>(.*?)</a>.*?"viewData.symbol".*?>(.*?)</td>'''
    data=re.findall(pattern,text,re.S)
    address=pandas.DataFrame(data,columns=['url','name','code'])
    address.set_index('code').to_csv('%s/InvestingURL.csv' % folder)
    return(address.set_index('code'))


if __name__ == '__main__':
    # setToken('13a8a6f82ca1f297acfc32c92a6c761b9e00de7ca61a0551fb2d0e62676d76d1')

    # updateAllStock(savePath)

    updateIndex()

    pass



