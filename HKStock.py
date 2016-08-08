import pandas
import tushare as ts


HKindex=['HSI','HSCEI','HSC','HSF','HSCCI','HSP','HSU']
mkt=ts.Market()


def setToken(token):
    ts.set_token(token)
    print(ts.get_token())

def getIndexData(tick):
    print('Requiring HK market data')
    data=mkt.MktIdxd(ticker=tick,field='ticker,tradeDate,openIndex,lowestIndex,highestIndex,closeIndex')

    return(data)


if __name__ == '__main__':
    # setToken('13a8a6f82ca1f297acfc32c92a6c761b9e00de7ca61a0551fb2d0e62676d76d1')



    for i in HKindex:

        indexData=getIndexData(i)

        indexData.to_excel('%s.xlsx' % i)
    # indexData=pandas.read_excel('%s.xlsx' % HKindex[1])


    print(indexData)

