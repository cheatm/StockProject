from PyQtTest import StockChart
import sys,pandas,time
import SaveData
import HKStock,indicator,DataTransform
from PyQt4 import QtGui,QtCore
import GUI.StockChart as ST


def showChart():
    app=QtGui.QApplication(sys.argv)
    stockChart=StockChart()

    HSI=HKStock.readIndexData(HKStock.HKindex[0],True)
    HSI=DataTransform.pandas_to_listSeries(HSI,'tradeDate','openIndex','highestIndex','lowestIndex','closeIndex')
    HSI[0]=DataTransform.timeList_to_secondList(HSI[0],'%Y-%m-%d')

    stockChart.importCandle(name=HKStock.HKindex[0]+'candle',candle=HSI,color='white')

    for i in range(0,6):

        data=HKStock.readIndexData(HKStock.HKindex[i],update=True)

        ind=indicator.MOMENTUM(data,60,'closeIndex')

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

    stockChart.show()
    sys.exit(app.exec_())

def showStockChart():
    app=QtGui.QApplication(sys.argv)
    stockChart=StockChart()

    # **********************************************************************************
    # code:代码
    code='0700.hk'
    # 读取股票数据
    data=HKStock.readStockData(code,db=HKStock.dbPath)
    # 将数据转换成candle格式:[[],[],[],[],[]]
    candle=DataTransform.pandas_to_listSeries(data,'time','Open','High','Low','Close')
    # 将时间由string装成数字
    # candle[0]=DataTransform.timeList_to_secondList(candle[0],'%Y-%m-%d')

    # 蜡烛图
    stockChart.importCandle(code,candle)

    # 将数据转化成柱图格式：[[],[]]
    volume=DataTransform.pandas_to_listSeries(data,'time','Volume')
    # 转换时间
    # volume[0]=DataTransform.timeList_to_secondList(volume[0],'%Y-%m-%d')

    # stockChart.importLine('Volume',volume,figure=1,color='cyan')
    # 柱图
    stockChart.importHistogram('Volume',volume,figure=1,color='cyan')

    # **********************************************************************************

    stockChart.show()
    sys.exit(app.exec_())

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

    stockChart.importCandle('0700.hk',df=data[['time','openIndex','highestIndex','lowestIndex','closeIndex']],color='cyan')
    stockChart.importLine('MA60',df=mal,color='red')
    stockChart.importLine('MA20',df=mas,color=[60,200,150])

    c=0
    for i in HKStock.HKindex:

        data=HKStock.read_sql(i,'HKindex')
        mom=indicator.momentum(data['time'],data['closeIndex'])
        stockChart.importLine(i,mom,n=1,color=c)
        c+=1
    stockChart.yLabel[1]=[100]

    stockChart.importHist('NewHigh-NewLow',time=T,hist=hl.tolist(),n=2,label=[0])
    stockChart.importHist('Raise-Fall',time=T,hist=rf.tolist(),n=3,label=[0])

    stockChart.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    # showChart()
    #
    # showStockChart()
    GUIStockChart()
