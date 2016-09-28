import pandas
import numpy,talib
from talib import abstract
import time,datetime,math

folder='ini'
fast=12
slow=26

def EMA(candle,period=12,price='close'):
    print('Caculating EMA period = %s' % period)
    data=[[candle.get_value(candle.index.tolist()[0],'date'),candle.get_value(candle.index.tolist()[0],'time'),candle.get_value(candle.index.tolist()[0],price)]]
    k=2/(period+1)
    for i in candle.index:
        today=candle.get_value(i,price)
        yest=data[-1]
        # date.append(candle.get_value(i,'date'))
        value=today*k+(1-k)*yest[2]
        # ema.append(value)
        data.append([candle.get_value(i,'date'),candle.get_value(i,'time'),value])

    data.pop(0)
    return pandas.DataFrame(data,columns=['date','time','value'])


def MA(time,price,period=60,matype=0,index=None,compare=False):
    ma=talib.MA(numpy.array(price),timeperiod=period,matype=matype)
    name='MA%s' % period
    if compare:
        name='C-'+name
        for i in range(0,len(ma)):
            v=ma[i]
            if not numpy.isnan(v):
                ma[i]=price[i]-v

    data=pandas.DataFrame({'time':time,name:ma}).dropna()
    data.insert(0,'time',data.pop('time'))
    if index is not None:
        return data.set_index(index)

    return data

def MACD(time,price,fast=12,slow=26,signal=9,index=None,out=None):
    input=numpy.array(price)
    d={}

    d['macd'],d['signal'],d['hist']=talib.MACD(input,fastperiod=fast,slowperiod=slow,signalperiod=signal)
    if out is not None:
        for k in d.copy().keys():
            if k not in out:
                d.pop(k)

    d['time']=time

    data=pandas.DataFrame(d).dropna()
    data.insert(0,'time',data.pop('time'))

    if index is not None:
        return data.set_index(index)

    return data

def ATR(time,high,low,close,period=14,index=None):

    atr=talib.ATR(numpy.array(high),numpy.array(low),numpy.array(close),timeperiod=period)
    data=pandas.DataFrame({'ATR%s' % period:atr,'time':time}).dropna()
    data.insert(0,'time',data.pop('time'))
    if index is not None:
        return data.set_index(index)

    return data

def ADX(time,high,low,close,period=14,index=None):

    adx=talib.ADX(numpy.array(high),numpy.array(low),numpy.array(close),timeperiod=period)
    data=pandas.DataFrame({'ADX%s' % period:adx,'time':time}).dropna()
    data.insert(0,'time',data.pop('time'))
    if index is not None:
        return data.set_index(index)

    return data

def RSI(time,price,period=14,index=None,columns=None):

    rsi=talib.RSI(numpy.array(price),timeperiod=period)
    data=pandas.DataFrame({'RSI%s' % period:rsi,'time':time}).dropna()
    data.insert(0,'time',data.pop('time'))
    if columns is not None:
        data.columns=columns

    if index is not None:
        return data.set_index(index)

    return data

def Correlation(price1,price2,time=None,period=30):
    if len(price1) != len(price2):
        print('price1 and price2 are not in the same length')
        return 0

    corr=talib.CORREL(numpy.array(price1),numpy.array(price2),timeperiod=period)
    data=pandas.DataFrame({'time':time,'corr':corr}).dropna()
    data.insert(0,'time',data.pop('time'))
    # if time is not None and len(time)==len(price1):
    #     data=pandas.DataFrame(corr,index=time).dropna()
    #
    #

    return data

def momentum(time,price,period=60):
    time = numpy.array(time)
    price = numpy.array(price)

    if len(time) != len(price):
        print("length of time and price not equal")
        return 0

    if period > len(price):
        print('period > length of data')
        return 0

    data=[]
    for i in range(period,len(price)):
        data.append([
            time[i],price[i]/price[i-period]*100
        ])

    return pandas.DataFrame(data,columns=['time','momentum%s' % period])

def MACD_Analisys(candle):

    print('Analisysing')
    r=candle.index.tolist()

    origin=[12,24,8]
    dist={'date':candle.date[r[0]:r[-1]].tolist()}
    for a in range(1,7):
        inp=[origin[0]*a/2,origin[1]*a/2,origin[2]*a/2,]
        macd=MACD(candle[r[0]:r[-1]],inp[0],inp[1],inp[2])
        ud=['U']
        for i in macd.index[1:len(macd.index)]:
            if macd.get_value(i,'Histogram')>macd.get_value(i-1,'Histogram'):
                ud.append('U')
            else:
                ud.append('D')
        dist[a/2]=ud
        print('a=%s done' % a)
    print(dist.keys())
    data=pandas.DataFrame(dist,columns=['date',0.5,1.0,1.5,2.0,2.5,3.0])
    return data

def MOMENTUM(candle,N,price='closePrice',dateIndex='tradeDate',timeFormat='%Y-%m-%d'):
    data=[]
    for i in candle.index[N:] :
        mome=candle.get_value(i,price)/candle.get_value(i-N,price)*100
        date=candle.get_value(i,dateIndex)
        tp=time.strptime(date,timeFormat)

        data.append([time.mktime(tp),date,mome])

    return (pandas.DataFrame(data,columns=['time',dateIndex,'MOMENTUM']) )

def RS_Ratio(time=None,data=None,basic=None,df=None,m=5):
    if df is not None:

        time=df[df.columns[0]].tolist()
        data=df[df.columns[1]].tolist()
        basic=df[df.columns[2]].tolist()
        pass

    data=numpy.array(data)
    basic=numpy.array(basic)
    if len(time)!=len(data) or len(time)!=len(basic):
        print('length not equal: %s, %s, %s,' % (len(time),len(data),len(basic)))
        return 0

    X=[]
    print(data)
    for i in range(0,len(time)):

        X.append(data[i]/basic[i])

    npx=numpy.array(X)

    mean=npx.mean()
    std=npx.std()

    for i in range(0,len(X)):
        X[i]=(X[i]-mean)/std+100

    out=pandas.DataFrame({'RS_Ratio':X,'time':time})
    out.insert(0,'time',out.pop('time'))

    moment=momentum(time,X,period=m)


    return out.merge(moment,how='outer',on='time').dropna()

def sentiment(time,price,n=14):
    if len(time)!=len(price):
        print('length not equal')
        return 0

    time=numpy.array(time)
    price=numpy.array(price)
    index=[]
    for i in range(0,n):
        index.append(None)

    for i in range(n,len(time)):
        high=max(price[i-n:i+1])
        low=min(price[i-n:i+1])
        index.append(100*(price[i]-low)/(high-low))

    out=pandas.DataFrame({'sentiment':index,'time':time})
    out.dropna(inplace=True)
    out.insert(0,'time',out.pop('time'))

    return out

def getIndicator(indicator,time,*inputs,names=None,**params):

    '''

    :param indicator: name of indicator in talib
    :param time: TimeArray in seconds
    :param names:

    :param values:
        datas to caculate,
        get more in TAlib_indicators.txt
    :param params:
        params to be used
        get more in TAlib_indicators.txt

    How to use:
        Find 'RSI' in TAlib_indicators.txt:
            ------------------------------------------------------------------------------------
            RSI:
            RSI([input_arrays], [timeperiod=14])

            Relative Strength Index (Momentum Indicators)

            Inputs:
                price: (any ndarray)
            Parameters:
                timeperiod: 14
            Outputs:
                real
            ------------------------------------------------------------------------------------

                                         (Inputs)                (Parameters)
        rsi=getIndicator('RSI',timelist,pricelist,names='RSI10',timeperiod=10)

    :return: DataFrame
    '''

    arrayValues=[]

    for v in inputs:
        if isinstance(v,numpy.ndarray):
            arrayValues.append(v)
        else:
            arrayValues.append(numpy.array(v))

    ind=getattr(talib,indicator)(*arrayValues,**params)

    if names is None:
        names=list(range(0,len(ind))) if isinstance(ind,tuple) else 0

    data={'time':time}
    if isinstance(ind,tuple):
        count=0
        for name in names:
            data[name]=ind[count]
            count+=1

        names.insert(0,'time')
    else:
        data[names]=ind
        names=['time',names]

    ind=pandas.DataFrame(data,columns=names).dropna()

    return ind


if __name__ == '__main__':

    pass