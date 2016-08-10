import pandas
import tushare as ts


HKindex=['HSI','HSCEI','HSC','HSF','HSCCI','HSP','HSU']
mkt=ts.Market()


def setToken(token):
    ts.set_token(token)
    print(ts.get_token())

def getIndexData(tick):
    print('Requiring index %s' % tick)
    data=mkt.MktIdxd(ticker=tick,field='ticker,tradeDate,openIndex,lowestIndex,highestIndex,closeIndex')

    return(data)

def getStockData():
    print('Requiring stock data')
    # data=mkt.MktEqud(ticker='600000')
    data=mkt.MktHKEqud(tradeDate='2016-08-10')
    return (data)


if __name__ == '__main__':
    # setToken('13a8a6f82ca1f297acfc32c92a6c761b9e00de7ca61a0551fb2d0e62676d76d1')

    # for i in HKindex:
    #
    #     indexData=getIndexData(i)
    #
    #     indexData.to_excel('%s.xlsx' % i)
    # # indexData=pandas.read_excel('%s.xlsx' % HKindex[1])
    #
    #
    # print(indexData)

    # print(getStockData())
    print(ts.get_token())
