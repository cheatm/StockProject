import pandas
import numpy,talib
from talib import abstract
import time,datetime

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

# def MACD(candle,fast=12,slow=26,signal=9):
#     print('Calulating MACD fast=%s slow=%s signal=%s' % (fast,slow,signal))
#     fastema=EMA(candle,fast)
#     slowema=EMA(candle,slow)
#     MACDline=fastema.value-slowema.value
#     MACDline.index=candle.index
#
#     start=candle.index.tolist()[0]
#     hist=[candle.get_value(start,'date'),candle.get_value(start,'time'),
#            MACDline[start],MACDline[start],0] #date/time/MACDline/signalLine/Histogram
#     histograms=[hist]
#
#     k=2/(signal+1)
#     for i in candle.index:
#         today=MACDline[i]
#         signalLine=today*k+(1-k)*hist[3]
#         hist=[candle.get_value(i,'date'),candle.get_value(i,'time'),
#             MACDline[i],signalLine,MACDline[i]-signalLine]
#         histograms.append(hist)
#
#     histograms.pop(0)
#
#
#     return pandas.DataFrame(histograms,columns=['date','time','MACDLine','Signal','Histogram'])

def MA(time,price,period=60,matype=0,index=None):
    ma=talib.MA(numpy.array(price),timeperiod=period,matype=matype)
    data=pandas.DataFrame({'time':time,'MA':ma}).dropna()

    if index is not None:
        return data.set_index(index)

    return data

def MACD(time,price,fast=12,slow=26,signal=9,index=None):
    input=numpy.array(price)
    macd,signal,hist=talib.MACD(input,fastperiod=fast,slowperiod=slow,signalperiod=signal)
    data=pandas.DataFrame({'time':time,'macd':macd,'signal':signal,'hist':hist}).dropna()

    if index is not None:
        return data.set_index(index)

    return data

def ATR(time,high,low,close,period=14,index=None):

    atr=talib.ATR(numpy.array(high),numpy.array(low),numpy.array(close),timeperiod=period)
    data=pandas.DataFrame({'ATR':atr,'time':time}).dropna()

    if index is not None:
        return data.set_index(index)

    return data

def ADX(time,high,low,close,period=14,index=None):

    adx=talib.ADX(numpy.array(high),numpy.array(low),numpy.array(close),timeperiod=period)
    data=pandas.DataFrame({'ADX':adx,'time':time}).dropna()

    if index is not None:
        return data.set_index(index)

    return data

def RSI(time,price,period=14,index=None):

    rsi=talib.RSI(numpy.array(price),timeperiod=period)
    data=pandas.DataFrame({'RSI':rsi,'time':time}).dropna()

    if index is not None:
        return data.set_index(index)

    return data

def Correlation(price1,price2,time=None,period=30):
    if len(price1) != len(price2):
        print('price1 and price2 are not in the same length')
        return 0

    corr=talib.CORREL(numpy.array(price1),numpy.array(price2),timeperiod=period)
    data=pandas.DataFrame(corr,index=time).dropna()
    # if time is not None and len(time)==len(price1):
    #     data=pandas.DataFrame(corr,index=time).dropna()
    #
    #

    return data


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

if __name__ == '__main__':
    pass