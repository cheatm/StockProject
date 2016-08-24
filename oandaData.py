from pyoanda import Client, TRADE
from oandapy import oandapy
import pandas,time,datetime
import sqlite3


folder='ini'
instruments='Instrument.txt'
granularity=['M15','H1','H4','D','W','M']
savePath=open('ini/OandaSavePath.txt').read()

opClient=oandapy.API(environment='live',
                     access_token="e94323526b351d296277869d207ccaec-2627af28b94aed9fd0749ab292a923c5")

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

def read_sql(table,code=None,dbpath=None,con=None):
    close=False

    if dbpath is None:
        dbpath='%s/%s.db' % (savePath,code)

    if con is None:
        con=sqlite3.connect(dbpath)
        close=True

    data=pandas.read_sql('''select * from "%s"''' % table,con)

    if close:
        con.close()

    return data

def save_sql(data,table,dbpath=None,con=None,if_exists='replace'):
    close=False
    if con is None:
        con=sqlite3.connect(dbpath)
        close=True

    data.to_sql(table,con,if_exists=if_exists)

    print('%s saved' % table)

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

def getCommitmentsOfTraders(instrument,client=opClient):
    '''

    :param instrument:
        Required Name of the instrument to retrieve Commitments of Traders data for.
        Supported instruments: AUD_USD, GBP_USD, USD_CAD, EUR_USD, USD_JPY,
                               USD_MXN, NZD_USD, USD_CHF, XAU_USD, XAG_USD.
    :param client:
    :return: Dataframe
    '''

    insts=['AUD_USD', 'GBP_USD', 'USD_CAD', 'EUR_USD', 'USD_JPY',
           'USD_MXN', 'NZD_USD', 'USD_CHF', 'XAU_USD', 'XAG_USD']

    if instrument not in insts:
        print('%s : not supported for Commitments of Traders' % instrument)
        return 0

    response=client.get_commitments_of_traders(instrument=instrument)
    data=pandas.DataFrame(response[instrument])

    timelist=[]
    for i in data.index:
        value=data.get_value(i,'date')
        timelist.append(value)
        date=datetime.datetime.fromtimestamp(value)
        data.set_value(i,'date',date)

    data.insert(0,'time',timelist)
    data.set_index('time',inplace=True)

    return data

def getHistoricalPositionRatios(instrument,period=31536000,client=opClient):
    '''

    :param instrument:
        Required Name of the instrument to retrieve historical position ratios for.
        Supported instruments: AUD_JPY, AUD_USD, EUR_AUD, EUR_CHF, EUR_GBP, EUR_JPY,
                               EUR_USD, GBP_CHF, GBP_JPY, GBP_USD, NZD_USD, USD_CAD,
                               USD_CHF, USD_JPY, XAU_USD, XAG_USD.
    :param period:
        Period of time in seconds to retrieve calendar data for.
        Values not in the following list will be automatically adjusted to the nearest valid value.
            86400 - 1 day - 20 minute snapshots
            172800 - 2 day - 20 minute snapshots
            604800 - 1 week - 1 hour snapshots
            2592000 - 1 month - 3 hour snapshots
            7776000 - 3 months - 3 hour snapshots
            15552000 - 6 months - 3 hour snapshots
            31536000 - 1 year - daily snapshots

    :param client:

    :return: DataFrame()
    '''

    insList=['AUD_JPY', 'AUD_USD', 'EUR_AUD', 'EUR_CHF', 'EUR_GBP', 'EUR_JPY','USD_CHF', 'USD_JPY',
             'EUR_USD', 'GBP_CHF', 'GBP_JPY', 'GBP_USD', 'NZD_USD', 'USD_CAD', 'XAU_USD', 'XAG_USD']

    if instrument not in insList:
        print('%s : not supported for Historical Position Ratio' % instrument)
        return 0

    response = client.get_historical_position_ratios(instrument=instrument,period=period)
    data=pandas.DataFrame(response['data'][instrument]['data'],columns=['time','long_position_ratio','exchange_rate'])

    timeList=[]
    for t in data['time']:
        timeList.append(datetime.datetime.fromtimestamp(t))
    data.insert(1,'datetime',timeList)

    return data.set_index('time')

def getCalendar(instrument,period=31536000,client=opClient):
    response = client.get_eco_calendar(instrument=instrument,period=period)
    calendar=pandas.DataFrame(response)

    columns=calendar.columns.tolist()
    columns[columns.index('timestamp')]='time'
    calendar.columns=columns

    dateList=[]
    for i in calendar.index:
        value=calendar.get_value(i,'time')
        dateList.append(datetime.datetime.fromtimestamp(value))

    calendar.insert(0,'datetime',dateList)

    return calendar.set_index('time')

if __name__ == '__main__':

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

    for i in Insts:
        dbpath='%s/%s.db' % (savePath,i)
        con=sqlite3.connect(dbpath)
        print(dbpath)

        cot=getCommitmentsOfTraders(i)
        if cot is not 0:
            save_sql(cot,'COT',con=con)


        hpr=getHistoricalPositionRatios(i)
        if hpr is not 0:
            save_sql(hpr,'HPR',con=con)

        con.close()


