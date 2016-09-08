import oandaData as od
from PyQtTest import StockChart
from PyQt4 import QtGui
import sys,datetime
import HKStock as hk

def showOandaData(code=None):
    app=QtGui.QApplication(sys.argv)
    chart=StockChart()

    insts=od.readInsts()

    if isinstance(code,int):
        code=insts[code]


    data=od.read_sql('D',code)
    cot=od.read_sql('COT',code)
    hpr=od.read_sql('HPR',code)

    col='s-l'
    if code.find('USD')>0:
        col='l-s'
    cot_=cot[col].tolist()
    cot_time=cot['time'].tolist()

    chart.importCandle(code,candle=[data.time.tolist(),data.openBid.tolist(),
                                    data.highBid.tolist(),data.lowBid.tolist(),data.closeBid.tolist()])

    chart.importHistogram('COT:%s' % col,[cot_time,cot_],1,color='cyan')
    chart.setYlabel(0,figure=1)
    hprtime=[]
    for t in hpr.time.tolist():
        hprtime.append(t-t%10)

    # chart.importHistogram('HPR:position_diff',[hprtime,hpr.position_diff.tolist()],2,color='green')
    # chart.setYlabel(0,figure=2)
    chart.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    showOandaData(0)
