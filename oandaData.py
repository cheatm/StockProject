from pyoanda import Client, TRADE
import pandas,time
import sqlite3

folder='Oanda'
instruments='Instrument.txt'

defautClient= Client(
            environment=TRADE,
            account_id="152486",
            access_token="e94323526b351d296277869d207ccaec-2627af28b94aed9fd0749ab292a923c5"
        )


def getInstrumentHistory(instrument,candle_format="midpoint",granularity='D', count=None,
            daily_alignment=None, alignment_timezone=None,
            weekly_alignment="Monday", start=None,end=None,client=defautClient,recursion=False):

    pdata=None
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
                end=None
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
            data=getInstrumentHistory(instrument,candle_format=candle_format,granularity=granularity, count=5000,
                                    daily_alignment=daily_alignment, alignment_timezone=alignment_timezone,
                                    weekly_alignment=weekly_alignment, start=start,end=end,client=client,recursion=True)
            return(data)




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

        print(time.localtime(oldendtime))

        if len(pdata.index)==5000:

            new = getInstrumentHistory(instrument,candle_format=candle_format,granularity=granularity, count=5000,
                                    daily_alignment=daily_alignment, alignment_timezone=alignment_timezone,
                                    weekly_alignment=weekly_alignment, start=time.localtime(oldendtime),end=end,client=client,recursion=True)


            return pdata.append(new)

        else: return pdata


    return (pdata)


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
        print(path)
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
    end=time.localtime()
    start=time.strptime('2000-01-01','%Y-%m-%d')
    granularity=['M15','H1','H4','D','W','M']
    Insts=readInsts()
    c=0

    for i in Insts[Insts.index('HK33_HKD'):]:
        con=sqlite3.connect('%s/%s.db' % (folder,i))
        print(i)
        for g in granularity[2:]:
            print(g)
            path='%s/%s.db' % (folder,i)
            save_sql(getInstrumentHistory(i,start=start,end=end,candle_format='bidask',granularity=g),g,con=con)
        con.close()

