from pyoanda import Client, TRADE
import pandas,time,datetime
import sqlite3

folder='ini'
instruments='Instrument.txt'
granularity=['M15','H1','H4','D','W','M']
savePath=open('ini/OandaSavePath.txt').read()

defautClient= Client(
            environment=TRADE,
            account_id="152486",
            access_token="e94323526b351d296277869d207ccaec-2627af28b94aed9fd0749ab292a923c5"
        )


def getInstrumentHistory(instrument,candle_format="bidask",granularity='D', count=None,
            daily_alignment=0, alignment_timezone='Etc/UTC',
            weekly_alignment="Monday", start=None,end=None,client=defautClient,recursion=False):
    '''

    :param instrument:
    :param candle_format:
    :param granularity:
    :param count:
    :param daily_alignment:
    :param alignment_timezone:
    :param weekly_alignment:
    :param start:
    :param end:
    :param client:
        See more:
            http://developer.oanda.com/rest-live/rates/#retrieveInstrumentHistory
    :param recursion: ignore this
    :return: DataFrame()
    '''

    pdata=None
    print(start)

    if recursion:
        data=client.get_instrument_history(
                instrument=instrument,
                candle_format=candle_format,
                granularity=granularity,
                count=count,
                daily_alignment=daily_alignment,
                alignment_timezone=alignment_timezone,
                weekly_alignment=weekly_alignment,
                start=start,
                end=end
            )
        pdata=pandas.DataFrame(data['candles'])

    else:
        try:
            data=client.get_instrument_history(
                instrument=instrument,
                candle_format=candle_format,
                granularity=granularity,
                count=count,
                daily_alignment=daily_alignment,
                alignment_timezone=alignment_timezone,
                weekly_alignment=weekly_alignment,
                start=start,
                end=end
            )
            pdata=pandas.DataFrame(data['candles'])

        except Exception as e:
            print(e)
            # 如果所需candle数 > 5000 则从start开始每5000根获取一次并合并数据，recursion=True
            if '5000' in str(e):
                data=getInstrumentHistory(instrument,candle_format=candle_format,granularity=granularity, count=5000,
                                        daily_alignment=daily_alignment, alignment_timezone=alignment_timezone,
                                        weekly_alignment=weekly_alignment, start=start,end=None,client=client,recursion=True)
                return(data)
            else : return 0

    timeSting=[]
    # 修改时间格式
    for i in pdata.index:
        t=pdata.get_value(i,'time')
        tSting=t.split('.')[0]
        timeSting.append(tSting)
        ti=time.strptime(tSting,'%Y-%m-%dT%H:%M:%S')
        pdata.set_value(i,'time',time.mktime(ti))

    pdata.set_index('time',inplace=True)
    pdata.drop('complete',1,inplace=True)

    column=pdata.columns.tolist()

    for i in pdata.index:
        for c in column:
            v=pdata.get_value(i,c)
            try:
                pdata.set_value(i,c,float(v))
            except Exception as e:
                print(e)


    pdata.insert(0,'Date',timeSting)

    if recursion:
        # 如果递归且当前数据=5000组 说明没有读取到结束位置的数据 则继续递归 由当前数据的最后一个作为start输入

        if len(pdata.index)==5000:
            oldendtime=pdata.index.tolist()[-1]
            startTime=datetime.datetime.fromtimestamp(oldendtime).strftime("%Y-%m-%dT%H:%M:%S.%f%z")

            new = getInstrumentHistory(instrument,candle_format=candle_format,granularity=granularity, count=5000,
                                    daily_alignment=daily_alignment, alignment_timezone=alignment_timezone,
                                    weekly_alignment=weekly_alignment, start=startTime,end=end,client=client,recursion=True)

            return pdata.append(new)

    return (pdata)

def update(dbpath,*granularity,instrument=None):
    '''

    :param dbpath: address to save
    :param granularity: 'M15','H1','H4','D','W','M'
    :param instrument: instrument to get
        If dbpath is named by instrument itself, instrument can be None
    :return: None
    '''

    con=sqlite3.connect(dbpath)

    if instrument is None:
        instrument=Split(dbpath,['/','.'])[-2]

    if len(granularity)==0:
        granularity=con.execute('''select name from sqlite_master where type='table' ''').fetchall()
        for i in range(0,len(granularity)):
            granularity[i]=granularity[i][0]

    for g in granularity:
        lastRecord=con.execute('''SELECT * FROM "%s" ORDER BY rowid DESC ''' % g).fetchone()
        startTime=datetime.datetime.fromtimestamp(lastRecord[0]).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        endTime=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        new=getInstrumentHistory(instrument,granularity=g,start=startTime,end=endTime)
        new.to_sql(g,con,if_exists='append')

    con.close()

def Split(word,seps):

    if len(seps)>1:
        w=word.split(seps[0])
        s=[]
        for i in w:
            s.extend(Split(i,seps[1:]))
        return(s)
    elif len(seps)==1:
        s=word.split(seps[0])
        while '' in s:
            s.remove('')
        return(s)
    # else: return []

def save_sql(data,table,dbpath=None,con=None,if_exists='replace'):
    close=False
    if con is None:
        con=sqlite3.connect(dbpath)
        close=True

    data.to_sql(table,con,if_exists=if_exists)


    if close:
        print(dbpath)
        con.close()

def readInsts():
    path='%s/%s' % (folder,instruments)
    file=open(path)
    lines=file.readlines()
    out=[]
    for l in lines:
        out.extend(Split(l,[',','\n']))

    file.close()

    return out


if __name__ == '__main__':
    # end=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    #
    # start=datetime.datetime(2001,1,1).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    #
    Insts=readInsts()
    #
    # path='E:/StockProject/Oanda'
    # for i in Insts:
    #     dbpath='%s/%s.db' % (path,i)
    #     print(dbpath)
    #     con=sqlite3.connect(dbpath)
    #
    #     for g in granularity[4:]:
    #         print(g)
    #         save_sql(getInstrumentHistory(i,start=start,end=end,candle_format='bidask',granularity=g),g,con=con)
    #
    #     con.close()

    print(savePath)
    update(savePath+Insts[0],'H4')
