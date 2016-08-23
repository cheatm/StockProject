from pyoanda import Client, TRADE
import pandas,time,datetime
import sqlite3

folder='Oanda'
instruments='Instrument.txt'
granularity=['M15','H1','H4','D','W','M']

defautClient= Client(
            environment=TRADE,
            account_id="152486",
            access_token="e94323526b351d296277869d207ccaec-2627af28b94aed9fd0749ab292a923c5"
        )


def getInstrumentHistory(instrument,candle_format="bidask",granularity='D', count=None,
            daily_alignment=0, alignment_timezone='Etc/UTC',
            weekly_alignment="Monday", start=None,end=None,client=defautClient,recursion=False):

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


        pass
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
            if '5000' in str(e):
                data=getInstrumentHistory(instrument,candle_format=candle_format,granularity=granularity, count=5000,
                                        daily_alignment=daily_alignment, alignment_timezone=alignment_timezone,
                                        weekly_alignment=weekly_alignment, start=start,end=None,client=client,recursion=True)
                return(data)
            else : return 0




    timeSting=[]

    for i in pdata.index:
        # 修改时间格式
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

        oldendtime=pdata.index.tolist()[-1]
        startTime=datetime.datetime.fromtimestamp(oldendtime).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        if len(pdata.index)==5000:

            new = getInstrumentHistory(instrument,candle_format=candle_format,granularity=granularity, count=5000,
                                    daily_alignment=daily_alignment, alignment_timezone=alignment_timezone,
                                    weekly_alignment=weekly_alignment, start=startTime,end=end,client=client,recursion=True)

            return pdata.append(new)

    return (pdata)

def update(dbpath,*granularity,instrument=None):
    con=sqlite3.connect(dbpath)

    if instrument is None:
        instrument=Split(dbpath,['/','.'])[-2]

    if len(granularity)==0:
        granularity=con.execute('''select name from sqlite_master where type='table' ''').fetchall()
        for i in range(0,len(granularity)):
            granularity[i]=granularity[i][0]

    for g in granularity:
        lastRecord=con.execute('''SELECT * FROM "%s" ORDER BY rowid DESC ''' % g).fetchone()
        startTime=datetime.date.fromtimestamp(lastRecord[0])
        new=getInstrumentHistory(instrument,granularity=g,start=startTime,end=datetime.date.today())
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

def test(instrument,start=None,end=None,count=None,client=defautClient):
    print(start)
    data=client.get_instrument_history(instrument, candle_format="midpoint",
                               granularity='D',count=count,daily_alignment=0,
                               weekly_alignment="Monday", alignment_timezone='Asia/Hong_Kong',
                               start=start
                               )

    return pandas.DataFrame(data['candles'])


if __name__ == '__main__':
    end=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")

    start=datetime.datetime(2001,1,1).strftime("%Y-%m-%dT%H:%M:%S.%f%z")

    granularity=['M15','H1','H4','D','W','M']
    Insts=readInsts()
    i=Insts[2]
    g=granularity[1]


    path='E:/StockProject/Oanda'
    for i in Insts:
        dbpath='%s/%s.db' % (path,i)
        print(dbpath)
        con=sqlite3.connect(dbpath)

        for g in granularity[4:]:
            print(g)
            # path='%s/%s.db' % (folder,i)
            save_sql(getInstrumentHistory(i,start=start,end=end,candle_format='bidask',granularity=g),g,con=con)

        con.close()

    # path='E:/StockProject/Oanda/GBP_USD.db'
    # update(path,'H4')
    # end=datetime.datetime.now()

