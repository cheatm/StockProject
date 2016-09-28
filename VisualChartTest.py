import sys,pandas,time
import SaveData
import HKStock,indicator
from PyQt4 import QtGui
import GUI.StockChart as ST
import oandaData as od

def GUIStockChart():
    app=QtGui.QApplication(sys.argv)
    stockChart=ST.StockChart()

    data=HKStock.readStockData('HSI','HKindex').dropna()
    mal=indicator.MA(data['time'],data['closeIndex'])
    mas=indicator.MA(data['time'],data['closeIndex'],period=20)
    yh=SaveData.readYahooDataFromSql('HK')['HK']
    rf=yh.Raise-yh.Fall
    hl=yh.NewHigh-yh.NewLow
    T=[]
    for d in yh['index']:
        T.append(time.mktime(time.strptime(d,'%Y/%m/%d')))

    stockChart.importCandle('HSI',df=data[['time','openIndex','highestIndex','lowestIndex','closeIndex']],color='cyan',label=2)
    stockChart.importLine('MA60',df=mal,color='red')
    stockChart.importLine('MA20',df=mas,color=[60,200,150])

    c=0
    for i in HKStock.HKindex:

        data=HKStock.read_sql(i,'HKindex')
        mom=indicator.momentum(data['time'],data['closeIndex'])
        stockChart.importLine(i,mom,n=1,color=c)
        c+=1
    stockChart.yLabel[1][0]=[100]

    stockChart.importHist('NewHigh-NewLow',time=T,hist=hl.tolist(),n=2,label=[0])
    stockChart.importHist('Raise-Fall',time=T,hist=rf.tolist(),n=3,label=[0])

    stockChart.show()
    sys.exit(app.exec_())

def oandaChart():
    app=QtGui.QApplication(sys.argv)
    forexChart=ST.StockChart()

    data=od.read_sql('D','EUR_USD')
    forexChart.importCandle('EUR_USD',df=data[['time','openBid','highBid','lowBid','closeBid']],label=4)

    forexChart.show()

    sys.exit(app.exec_())

if __name__ == '__main__':

    GUIStockChart()
    # oandaChart()