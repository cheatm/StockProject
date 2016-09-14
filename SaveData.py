
import EconomicData
import pandas
import time,datetime
import sqlite3
import os


DBName='YahooData.db'

file=open('ini/YHpath')
path=file.read()
fullDBPath=path+'/'+DBName
file.close()

now=time.time()
today=datetime.date.today()
todaystr=today.strftime('%Y/%m/%d')
yesterday=datetime.date.today()-datetime.timedelta(1)
yesterdaystr=yesterday.strftime('%Y/%m/%d')
lastFriday=datetime.date.today()-datetime.timedelta(3-datetime.date.today().weekday())
lastFridaystr=lastFriday.strftime('%Y/%m/%d')

def createPath(path=path):
    if os.path.exists(path):
        return

    os.makedirs(path)


def saveYahooData(date=None,conn=None,**market):
    close=False
    if date==None:
        date=todaystr

    if conn is None:
        conn=sqlite3.connect(fullDBPath)
        close=True

    # read dara from Yahoo
    data=EconomicData.getYahooData()

    for m in market.keys():
        mkdata=pandas.DataFrame([data.loc[m]],index=[market[m]])
        print(m)
        print(mkdata)
        mkdata.to_sql(m,conn,if_exists='append')

    if close:
        conn.close()
    time.sleep(5)

def readYahooDataFromSql(*market,conn=None):
    close=False
    if conn is None:
        conn=sqlite3.connect(fullDBPath)
        close=True

    outData={}
    for m in market:
        data=pandas.read_sql('''select * FROM %s''' % m , conn)

        outData[m]=data
    if close:
        conn.close()

    return outData


def changeYahooData():
    conn=sqlite3.connect(fullDBPath)
    # conn.execute('''update NASDAQ set rowid = 14 where rowid == 15''')
    # conn.execute('''select 'index' from HK''')
    # conn.execute('''DELETE FROM NASDAQ WHERE ROWID == 14''')
    # conn.execute('''DELETE FROM HK WHERE ROWID == 12''')

    readYahooDataFromSql('HK','NASDAQ',conn=conn)

    conn.close()

if __name__ == '__main__':

    createPath()

    if today.weekday() is not 0:
        saveYahooData(NASDAQ=yesterdaystr,HK=todaystr)
    else:
        saveYahooData(NASDAQ=lastFridaystr,HK=todaystr)

    # saveYahooData(NASDAQ=yesterdaystr)
    # saveYahooData(HK=todaystr)

    # changeYahooData()

    history=readYahooDataFromSql('HK','NASDAQ')
    print(history)




