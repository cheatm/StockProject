__author__ = 'CaiMeng'

import EconomicData
import pandas
import time,datetime
import sqlite3
import os

DBName='YahooData.db'
dirPath='D:/StockData'
# fullDBPath=dirPath+'/'+DBName
fullDBPath=DBName

now=time.time()
today=time.localtime(now)
todaystr=time.strftime('%Y/%m/%d',today)
yesterday=time.localtime(now-86400)
yesterdaystr=time.strftime('%Y/%m/%d',yesterday)



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

    for m in market:
        data=pandas.read_sql('''select * FROM %s''' % m , conn)
        print(data)
        UnKnown=conn.execute('''SELECT * FROM %s WHERE  "index" == "%s" ''' % (m,'2016/08/02')).fetchall()
        print(len(UnKnown))
    if close:
        conn.close()


def changeYahooData():
    conn=sqlite3.connect(fullDBPath)
    # conn.execute('''update NASDAQ set rowid = 14 where rowid == 15''')
    # conn.execute('''select 'index' from HK''')
    # conn.execute('''DELETE FROM NASDAQ WHERE ROWID == 14''')
    # conn.execute('''DELETE FROM HK WHERE ROWID == 12''')
    conn.commit()

    readYahooDataFromSql('HK','NASDAQ',conn=conn)

    conn.close()

if __name__ == '__main__':
    # test()
    createDataBase()

    saveYahooData(NASDAQ=yesterdaystr,HK=todaystr)
    #saveYahooData(NASDAQ=yesterdaystr)
    # saveYahooData(HK=todaystr)

    # changeYahooData()

    readYahooDataFromSql('HK')



