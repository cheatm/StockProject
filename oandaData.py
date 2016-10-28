from pyoanda import Client, TRADE
from oandapy import oandapy
import pandas,time,datetime,math
import sqlite3,os,threadpool
import indicator,numpy
import json


folder='ini'
instruments='Instrument.txt'
granularity=['M15','H1','H4','D','W','M']
savePath=open('ini/OandaSavePath.txt').read()
Clients=json.load(open('ini/OandaClient.json'))

opClient=None
defautClient=None

def createOpClient(opClient=opClient):
    if opClient is not None:
        return opClient


    opClient=oandapy.API(**Clients['oandapy'])

    return opClient

def creatDefaultClient(client=defautClient):
    if client is not None:
        return client

    client=Client(**Clients['pyoanda'])

    return client


def getInstrumentHistory(instrument,candle_format="bidask",granularity='D', count=None,
            daily_alignment=0, alignment_timezone='Etc/UTC',
            weekly_alignment="Monday", start=None,end=None,client=defautClient,recursion=False,con=None):
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


    client=creatDefaultClient(client)

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
            print('Error:93',e)
            # 如果所需candle数 > 5000 则从start开始每5000根获取一次并合并数据，recursion=True
            if '5000' in str(e):
                data=getInstrumentHistory(instrument,candle_format=candle_format,granularity=granularity, count=5000,
                                        daily_alignment=daily_alignment, alignment_timezone=alignment_timezone,
                                        weekly_alignment=weekly_alignment, start=start,end=None,client=client,recursion=True)
                if con is not None:
                    save_sql(data,granularity,con=con)
                    return 0

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

    if con is not None:
        save_sql(pdata,granularity,con=con)
        return 0

    return (pdata)

def update(*granularity,dbpath=None,instrument=None,con=None):
    '''
    update candle chart
    :param dbpath: address to save
    :param granularity: 'M15','H1','H4','D','W','M'
    :param instrument: instrument to get
        If dbpath is named by instrument itself, instrument can be None
    :return: None
    '''

    error=[]
    close=False

    if dbpath is None:
        dbpath='%s/%s.db' % (savePath,instrument)

    if con is None:

        con=sqlite3.connect(dbpath)
        close=True

    if instrument is None:
        instrument=Split(dbpath,'/','.')[-2]

    if len(granularity)==0:
        # granularity=con.execute('''select name from sqlite_master where type='table' ''').fetchall()
        granularity=['M15','H1','H4','D','W','M']

    for g in granularity:
        print (g)
        try:
            lastRecord=con.execute('''SELECT * FROM "%s" ORDER BY rowid DESC ''' % g).fetchone()
            start=datetime.datetime.fromtimestamp(lastRecord[0])
            startTime=start.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
            endTime=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")
            new=getInstrumentHistory(instrument,granularity=g,start=startTime,end=endTime)

            new[new.index>lastRecord[0]].to_sql(g,con,if_exists='append')
        except Exception as e:
            print('error_181:',e)
            error.append(g)

    if close:
        con.close()
    return  error

def Split(word,*seps,outType='str'):

    if len(seps)>1:
        w=word.split(seps[0])
        s=[]
        for i in w:
            s.extend(Split(i,*seps[1:]))

        if outType is 'int':
            for i in range(0,len(s)):
                s[i]=int(s[i])
        return(s)
    elif len(seps)==1:
        s=word.split(seps[0])

        while '' in s:
            s.remove('')
        return(s)
    # else: return []

def read_sql(table,code=None,dbpath=None,con=None):
    '''
    only 1 is in need
        :param table:
        :param code:
        :param dbpath:
    :param con:
    :return:

    How to use:
        data=read_sql('D',code='EUR_USD')
        data=read_sql('D',dbpath='.../.../EUR_USD/.db')
        data=read_sql('D',con=sqlite3.connect('.../.../EUR_USD/.db'))
    '''
    close=False

    if dbpath is None:
        dbpath='%s/%s.db' % (savePath,code)

    if con is None:
        con=sqlite3.connect(dbpath)
        close=True

    data=pandas.read_sql('''select * from %s''' % table,con)

    if close:
        con.close()

    return data

def save_sql(data,table,dbpath=None,con=None,if_exists='replace'):
    '''

    :param data:
    :param table:
    :param dbpath:
    :param con:
    :param if_exists:
    :return:

    How to use:
        data=getInstrumentHistory(.....)
        save_sql(data,'D',code='EUR_USD')
        save_sql(data,'D',dbpath='.../.../EUR_USD.db')
        save_sql(data,'D',con=sqlite3.connect('.../.../EUR_USD.db'))

    '''
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
    '''

    :return: list of instruments : ['EUR_USD','GBP_USD',...]
    '''
    path='%s/%s' % (folder,instruments)
    file=open(path)
    lines=file.readlines()
    out=[]
    for l in lines:
        out.extend(Split(l,',','\n'))

    file.close()

    return out

def getCommitmentsOfTraders(instrument,client=opClient,start=None,con=None):
    '''

    :param instrument:
        Required Name of the instrument to retrieve Commitments of Traders data for.
        Supported instruments: AUD_USD, GBP_USD, USD_CAD, EUR_USD, USD_JPY,
                               USD_MXN, NZD_USD, USD_CHF, XAU_USD, XAG_USD.
    :param client:
    :return: Dataframe
    '''

    client=createOpClient(client)

    insts=['AUD_USD', 'GBP_USD', 'USD_CAD', 'EUR_USD', 'USD_JPY',
           'USD_MXN', 'NZD_USD', 'USD_CHF', 'XAU_USD', 'XAG_USD']

    if instrument not in insts:
        print('%s : not supported for Commitments of Traders' % instrument)
        return 0

    response=client.get_commitments_of_traders(instrument=instrument)
    data=pandas.DataFrame(response[instrument])

    timelist=[]
    longshort=[]
    shortlong=[]
    publish=[]
    diff=[0]

    for i in data.index:
        value=data.get_value(i,'date')

        timelist.append(value)
        publish.append(value+4*24*60*60)

        ls=float(data.get_value(i,'ncl'))-float(data.get_value(i,'ncs'))

        longshort.append(ls)
        shortlong.append(-ls)

        try:
            diff.append(-ls-shortlong[-2])
        except :
            pass

        date=datetime.datetime.fromtimestamp(value)
        data.set_value(i,'date',date)

    data.insert(0,'time',timelist)
    data.insert(0,'publish',publish)
    data.insert(5,'l-s',longshort)
    data.insert(6,'s-l',shortlong)
    data.insert(7,'s-l_diff',diff)

    if start is not None:
        return data[data.time>=start].set_index('time')

    data.set_index('time',inplace=True)

    if con is not None:
        save_sql(data,'COT',con=con)
        return 0

    return data

def getHistoricalPositionRatios(instrument,period=31536000,client=opClient,start=None,con=None):
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

    client=createOpClient(client)

    insList=['AUD_JPY', 'AUD_USD', 'EUR_AUD', 'EUR_CHF', 'EUR_GBP', 'EUR_JPY','USD_CHF', 'USD_JPY',
             'EUR_USD', 'GBP_CHF', 'GBP_JPY', 'GBP_USD', 'NZD_USD', 'USD_CAD', 'XAU_USD', 'XAG_USD']

    if instrument not in insList:
        print('%s : not supported for Historical Position Ratio' % instrument)
        return 0

    response = client.get_historical_position_ratios(instrument=instrument,period=period)
    data=pandas.DataFrame(response['data'][instrument]['data'],columns=['time','long_position_ratio','exchange_rate'])

    if start is not None:
        data=data[data.time>start]

    timeList=[]
    for t in data['time']:
        d=datetime.datetime.fromtimestamp(t)
        timeList.append(datetime.datetime.fromtimestamp(t))


    spr=[]
    position=[]
    posdiff=[0]
    for l in data['long_position_ratio']:
        spr.append(100-l)
        position.append(spr[-1]-l)
        try:
            posdiff.append(position[-2]-position[-1])
        except:
            pass


    data.insert(1,'datetime',timeList)
    data.insert(3,'short_position_ratio',spr)
    data.insert(4,'position',position)
    data.insert(5,'position_diff',posdiff)

    if con is not None:
        save_sql(data.set_index('time'),'HPR',con=con)
        return 0

    return data.set_index('time')

def getCalendar(instrument,period=31536000,client=opClient):
    client=createOpClient(client)

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

def createFactorsTable(instrument=None,dbpath=None,con=None,**factors):
    '''
    Only have to input on of these 3:
        :param instrument:
        :param dbpath:
        :param con:
    :param factors: No use temporarily
    :return:

    How to use:
        createFactorsTable(instrument='EUR_USD')
        -------------------------------------------------------------
        createFactorsTable(dbpath='E:/FinanceData/Oanda/EUR_USD.db')
        -------------------------------------------------------------
        con=sqlite3.connect('E:/FinanceData/Oanda/EUR_USD.db')
        createFactorsTable(con=con)
        con.close()

    '''

    close=False

    if len(factors)==0:
        factors={
            'D':['time','closeBid','highBid','lowBid'],
            'COT':['publish','s-l','s-l_diff'],
            'HPR':['time','position','position_diff']
        }

    if dbpath is None:
        dbpath='%s/%s.db' % (savePath,instrument)

    print(dbpath)

    if con is None:
        con=sqlite3.connect(dbpath)
        close=True

    data={}
    start=0
    for k in factors.keys():
        f=factors[k]

        data[k]=read_sql(k,con=con).get(f)
        startTime=data[k].get_value(0,f[0])
        if start<startTime:
            start=startTime

    data['COT'].columns=['time','s-l','s-l_diff']

    if close:
        con.close()

    price=data['D']

    momentum=indicator.momentum(price['time'],price['closeBid'],period=60)
    data['momentumfast']=momentum
    momentum=indicator.momentum(price['time'],price['closeBid'],period=130)
    data['momentumslow']=momentum
    data['atr']=indicator.ATR(price['time'],price['highBid'],price['lowBid'],price['closeBid'],period=10)
    data['mafast']=indicator.MA(price['time'],price['closeBid'],period=60,compare=True)
    data['maslow']=indicator.MA(price['time'],price['closeBid'],period=130,compare=True)
    adx=indicator.ADX(price['time'],price['highBid'],price['lowBid'],price['closeBid'],period=10)
    data['ADX']=adx
    data['RSI']=indicator.RSI(price['time'],price['closeBid'],period=10)
    data['MACD']=indicator.MACD(price['time'],price['closeBid'],out=['hist'])
    histdiff=[0]
    for h in data['MACD'].index.tolist()[1:]:
        histdiff.append(data['MACD'].get_value(h,'hist')-data['MACD'].get_value(h-1,'hist'))
    data['MACD'].insert(2,'hist_diff',histdiff)


    data['ADX-mom']=indicator.momentum(adx['time'],adx['ADX%s' % 10],period=5)
    data['ADX-mom'].columns=['time','ADX-mom']

    data.pop('D')



    out=None
    for k in sorted(data.keys()):
        # if k == 'D':
        #     continue

        v=data[k]
        select=v[v.time>=start]
        for i in select.index:
            t=select.get_value(i,'time')

            select.set_value(i,'time',datetime.date.fromtimestamp(t))
        # print(select)
        if out is None:
            out=select.drop_duplicates('time').set_index('time')

        else:
            out=out.join(select.drop_duplicates('time').set_index('time'),how='outer')

    for c in out.columns:
        former=out.get_value(out.index.tolist()[0],c)
        for t in out.index.tolist()[1:]:
            v=out.get_value(t,c)
            # print(t,c,v,type(v))
            if math.isnan(v):
                out.set_value(t,c,former)
            former=out.get_value(t,c)

    return out.dropna()


def changeData(table,instrument=None,dbpath=None):
    '''
    Do not run this function!!!
    It's only for changing static data temporarily

    :param table:
    :param instrument:
    :param dbpath:
    :return:
    '''

    if dbpath is None:
        dbpath='%s/%s.db' % (savePath,instrument)

    con=sqlite3.connect(dbpath)

    try:
        data=read_sql(table,con=con)
        data.drop_duplicates('time').set_index('time').to_sql(table,con,if_exists='replace')
    except Exception as e:
        print(e)
        con.close()
        return 0

    # save_sql(data.set_index('time'),table,con=con)

    con.close()


def factorToScore(insts):
    '''

    :param insts: list of instruments:['EUR_USD','USD_CAD',....]
    :return: print(pandas.DataFrame(scoretable of all instruments in insts))
    '''

    score=[]
    for i in insts:
        data=read_sql('Factors',i)
        index=data.index.tolist()[-1]
        out=data[data.index==index]
        sldiff=0

        if out.get_value(index,'s-l_diff')<-1000:
            sldiff=-1
        elif out.get_value(index,'s-l_diff')>1000:
            sldiff=1

        posdiff=0
        if out.get_value(index,'position_diff')<-0.5:
            posdiff=-1
        elif out.get_value(index,'position_diff')>0.5:
            posdiff=1

        hist=0
        if out.get_value(index,'hist')>0 and out.get_value(index,'hist_diff')<0:
            hist=-1
        elif out.get_value(index,'hist')<0 and out.get_value(index,'hist_diff')>0:
            hist=1

        MA=0

        if out.get_value(index,'C-MA60')>out.get_value(index,'C-MA130'):
            if out.get_value(index,'C-MA60')<0 and out.get_value(index,'C-MA130')<0:
                MA=-1
        elif out.get_value(index,'C-MA60')<out.get_value(index,'C-MA130'):
            if out.get_value(index,'C-MA60')>0 and out.get_value(index,'C-MA130')>0:
                MA=1

        mom=0
        sm=out.get_value(index,'momentum60')
        lm=out.get_value(index,'momentum130')
        if lm<0 and sm>0:
            mom=-1
        if lm>0 and sm<0 and (-sm)>lm:
            mom=-1
        if lm>0 and sm<0:
            mom=1
        if lm<0 and sm>0 and sm>(-lm):
            mom=1

        rsi='Central area'
        if out.get_value(index,'RSI10')<40:
            rsi='Oversold'
        elif out.get_value(index,'RSI10')>60:
            rsi='Overbougut'

        adx='Consolidate'
        ADX=out.get_value(index,'ADX10')
        ADXm=out.get_value(index,'ADX-mom')
        if ADX>25 :
            if ADXm>100:
                adx='Trend'
            else:
                adx='Counter Trend'

        atr=out.get_value(index,'ATR10')

        score.append([i,sldiff,posdiff,hist,MA,mom,rsi,adx,atr*0.35,sldiff+posdiff+hist+MA++mom])
        # print(score)

    data=pandas.DataFrame(score,columns=[
        'Symbol','S-L_diff','Position_diff','hist & hist_diff','C-MA60 && C-MA130',
        'Momentum 60 & Momentum 130','RSI','ADX & ADX_Momentum','ATR:ATR*0.35','score'])
    print(data)

def updateCOT(instrument,dbpath=None,con=None):
    close=False

    if dbpath is None:
        dbpath='%s/%s.db' % (savePath,instrument)

    if con is None:
        con=sqlite3.connect(dbpath)
        close=True

    try:
        last=read_sql('COT',con=con)
        new=getCommitmentsOfTraders(instrument,start=last['publish'].tolist()[-1])

        new=last.append(new)
        save_sql(new,'COT',con=con)
    except:
        data=getCommitmentsOfTraders(instrument)
        save_sql(data,'COT',con=con)

    if close:
        con.close()

def updateHPR(instrument,dbpath=None,con=None):
    insList=['AUD_JPY', 'AUD_USD', 'EUR_AUD', 'EUR_CHF', 'EUR_GBP', 'EUR_JPY','USD_CHF', 'USD_JPY',
             'EUR_USD', 'GBP_CHF', 'GBP_JPY', 'GBP_USD', 'NZD_USD', 'USD_CAD', 'XAU_USD', 'XAG_USD']
    if instrument not in insList:
        return 0


    close=False

    if dbpath is None:
        dbpath='%s/%s.db' % (savePath,instrument)

    if con is None:
        con=sqlite3.connect(dbpath)
        close=True

    try:
        last=read_sql('HPR',con=con)
        new=getHistoricalPositionRatios(instrument,start=last['time'].tolist()[-1])
        new=last.drop(last.index.tolist()[-1]).set_index('time').append(new)
        save_sql(new,'HPR',con=con)
    except:
        data=getHistoricalPositionRatios(instrument)
        save_sql(data,'HPR',con=con)

    if close:
        con.close()

def importNewInstrument(instrument,*granularity,path=savePath,con=None):
    '''

    :param instrument: 'EUR_USD', 'AUD_USD' ...
    :param granularity: 'M15','H1','H4','D','W','M'
        If import nothing: granularity=['M15','H1','H4','D','W','M']
    :param path: default to savepath oanda
    :param con: None
        Will be created by path and instrument
    :return:
        Automatically save history data and COT and HPR data of a new instrument
        witch does not have any data in path 'oanda'
    '''


    if len(granularity) ==0:
        granularity=['M15','H1','H4','D','W','M']

    dbpath='%s/%s.db' % (path,instrument)
    print(dbpath)
    if os.path.exists(dbpath):
        print(instrument,' data already exists \nPlease try update(), updateCOT() or updateHPR()')
        return


    try:
        con=sqlite3.connect(dbpath)
    except :
        os.makedirs(path,exist_ok=True)
        time.sleep(1)
        con=sqlite3.connect(dbpath)


    start=datetime.date(1971,1,1).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    end=datetime.date.today().strftime("%Y-%m-%dT%H:%M:%S.%f%z")

    pool=threadpool.ThreadPool(6)

    def save(req,out):
        kwds=req.kwds
        if kwds is not None:
            save_sql(out,kwds['granularity'],con=con)

    for g in granularity:
        wrequest=threadpool.WorkRequest(getInstrumentHistory,
                                        kwds={'instrument':instrument,'granularity':g,
                                        'start':start,'end':end},
                                        callback=save)

        pool.putRequest(wrequest)

    def saveCOT(req,out):
        save_sql(out,'COT',con=con)

    pool.putRequest(
        threadpool.WorkRequest(getCommitmentsOfTraders,[instrument],callback=saveCOT)
    )

    def saveHPR(req,out):
        save_sql(out,'HPR',con=con)

    pool.putRequest(
        threadpool.WorkRequest(getHistoricalPositionRatios,[instrument],callback=saveHPR)
    )

    pool.wait()

    factors=createFactorsTable(instrument,con=con)
    save_sql(factors,'Factors',con=con)

    con.close()


if __name__ == '__main__':
    print(getInstrumentHistory('GBP_USD'))
    pass


