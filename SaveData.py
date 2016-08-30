__author__ = 'CaiMeng'

import EconomicData
import pandas
import time,datetime
import sqlite3
import os
import matplotlib.pyplot as plt

DBName='YahooData.db'
dirPath='D:/StockData'
# fullDBPath=dirPath+'/'+DBName

file=open('ini/YHpath')
fullDBPath=file.read()+'/'+DBName
file.close()

now=time.time()
today=time.localtime(now)
todaystr=time.strftime('%Y/%m/%d',today)
yesterday=time.localtime(now-86400)
yesterdaystr=time.strftime('%Y/%m/%d',yesterday)
# test


def dataBaseTest():
    name='testDB'
    conn=sqlite3.connect(name)
    conn.execute('''  ''')

    conn.close()

    pass

def createDataBase():
    # if dirPath doesnt exist, create a dirPath
    if not os.path.exists(dirPath):
        os.mkdir(dirPath)
    else:
        # if target DataBase file dosent exist, create a DataBase file
        if not os.path.exists(fullDBPath):

            connection=sqlite3.connect(fullDBPath)


            connection.close()
            print('close')


def readData(table,index_col=None,conn=None):
    if conn==None:
        conn=sqlite3.connect(fullDBPath)

        data=pandas.read_sql('select * from "%s" ' % table,conn,index_col=index_col)
    # print(data)
        conn.close()
        return(data)
    else:
        data=pandas.read_sql('select * from "%s" ' % table,conn,index_col=index_col)
        return (data)

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
        # print(data)
        # UnKnown=conn.execute('''SELECT * FROM %s WHERE  "index" == "%s" ''' % (m,'2016/08/02')).fetchall()
        # print(len(UnKnown))
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
    conn.commit()

    readYahooDataFromSql('HK','NASDAQ',conn=conn)

    conn.close()

def drawLine():
    data=readYahooDataFromSql('HK')
    data=data['HK']
    # print(data)
    date=[]
    RmF=[]
    HmL=[]

    for i in data.index:
        t=time.mktime(time.strptime(data.get_value(i,'index'),'%Y/%m/%d'))
        rf=data.get_value(i,'Raise')-data.get_value(i,'Fall')
        hl=data.get_value(i,'NewHigh')-data.get_value(i,'NewLow')
        date.append(t )
        RmF.append(rf)
        HmL.append(hl)
    print(date)
    print(RmF)
    print(HmL)

    plt.hold(True)
    plt.plot(date,RmF)
    plt.plot(date,HmL)
    plt.legend(['Raise-Fall','High-Low'])
    plt.show()

    pass

if __name__ == '__main__':
    # test()
    createDataBase()

    saveYahooData(NASDAQ=yesterdaystr,HK=todaystr)
    # saveYahooData(NASDAQ=yesterdaystr)
    # saveYahooData(HK=todaystr)

    # changeYahooData()

    print(readYahooDataFromSql('HK','NASDAQ'))
    # drawLine()



