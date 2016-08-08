from PyQtTest import StockChart
import sys,pandas,time
import SaveData
import HKStock,indicator
from PyQt4 import QtGui,QtCore

def showChart():
    app=QtGui.QApplication(sys.argv)
    stockChart=StockChart()

    HSI=pandas.read_excel('%s.xlsx' % HKStock.HKindex[0])
    date=[]
    for d in HSI.tradeDate:
        date.append(time.mktime(time.strptime(d,'%Y-%m-%d')))

    stockChart.importCandle(name=HKStock.HKindex[0],candle=[
        date,HSI.openIndex.tolist(),HSI.highestIndex.tolist(),HSI.lowestIndex.tolist(),HSI.closeIndex.tolist()
    ])

    for i in range(0,6):


        data=pandas.read_excel('%s.xlsx' % HKStock.HKindex[i])
        ind=indicator.MOMENTUM(data,60,'closeIndex')

        date=[]
        for d in data.tradeDate:
            date.append(time.mktime(time.strptime(d,'%Y-%m-%d')))

        stockChart.importLine(name=HKStock.HKindex[i],line=[ind.time.tolist(),ind.MOMENTUM.tolist()],figure=1)

    data=SaveData.readYahooDataFromSql('HK')['HK']

    # print(data)
    RmF=[]
    HmL=[]
    date=[]
    for i in data.index:
        t=time.mktime(time.strptime(data.get_value(i,'index'),'%Y/%m/%d'))
        rf=data.get_value(i,'Raise')-data.get_value(i,'Fall')
        hl=data.get_value(i,'NewHigh')-data.get_value(i,'NewLow')
        date.append(t )
        RmF.append(rf)
        HmL.append(hl)
    print(date)
    print(RmF)
    print(HmL)

    zero=[]
    for d in date:
        zero.append(0)
    stockChart.importLine('Raise-Fall',line=[
        date,RmF
    ],figure=2)
    stockChart.importLine('ZeroLine',line=[
        date,zero
    ],figure=2)
    stockChart.importLine('NewHigh-NewLow',line=[
        date,HmL
    ],figure=3)
    stockChart.importLine('ZeroLine',line=[
        date,zero
    ],figure=3)

    stockChart.importExtraLine([date[-5],0],[date[-1],2],3)

    stockChart.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    showChart()

