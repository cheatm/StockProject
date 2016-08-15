from PyQtTest import StockChart
import sys,pandas,time
import SaveData
import HKStock,indicator,DataTransform
from PyQt4 import QtGui,QtCore

def showChart():
    app=QtGui.QApplication(sys.argv)
    stockChart=StockChart()

    HSI=HKStock.readIndexData(HKStock.HKindex[0],True)
    HSI=DataTransform.pandas_to_listSeries(HSI,'tradeDate','openIndex','highestIndex','lowestIndex','closeIndex')
    HSI[0]=DataTransform.timeList_to_secondList(HSI[0],'%Y-%m-%d')
    # date=[]
    # for d in HSI.tradeDate:
    #     date.append(time.mktime(time.strptime(d,'%Y-%m-%d')))

    stockChart.importCandle(name=HKStock.HKindex[0]+'candle',candle=HSI,color='white')

    for i in range(0,6):

        data=HKStock.readIndexData(HKStock.HKindex[i],update=True)

        ind=indicator.MOMENTUM(data,60,'closeIndex')

        # date=[]
        # for d in data.tradeDate:
        #     date.append(time.mktime(time.strptime(d,'%Y-%m-%d')))

        stockChart.importLine(name=HKStock.HKindex[i],line=DataTransform.pandas_to_listSeries(ind,'time','MOMENTUM'),figure=1)

    data=SaveData.readYahooDataFromSql('HK')['HK']


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
    stockChart.setYlabel(100,figure=1)
    stockChart.setYlabel(110,figure=1)

    stockChart.importLine('Raise-Fall',line=[
        date,RmF
    ],figure=2)

    stockChart.setYlabel(0,figure=2)
    stockChart.importLine('NewHigh-NewLow',line=[
        date,HmL
    ],figure=3)
    stockChart.setYlabel(0,figure=3)


    # stockChart.importExtraLine([date[-5],0],[date[-1],2],3)

    stockChart.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    showChart()
    # listSeries=DataTransform.pandas_to_listSeries(HKStock.readIndexData(HKStock.HKindex[2],False),'tradeDate','closeIndex')
    # print(DataTransform.timeList_to_secondList(listSeries[0],'%Y-%m-%d'))
