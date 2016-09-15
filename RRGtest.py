from PyQtTest import RRG_M
from PyQt4 import QtGui
import sys,pandas
import oandaData,indicator,HKStock

def showRRG_M(**data):
    app=QtGui.QApplication(sys.argv)
    rrg=RRG_M()

    for k in data.keys():
        rrg.importData(k,DF=data[k])
        # rrg.importPrice(k,data[k]['time'],data[k]['closeBid'])
    rrg.show()
    sys.exit(app.exec_())

def getData():
    # insts=oandaData.readInsts()
    data={}
    # for i in insts[0:5]:
    #     data[i]=oandaData.read_sql('D',i)
    data2=HKStock.readStockData('HSI','HKindex')
    data2=data2.tail(15)
    data1=HKStock.readStockData('Day','0700.hk')
    data1=data1.tail(15)
    data0=data1.merge(data2,how='inner',on='time')
    print(data0[['time','Close','closeIndex']])

    rs=indicator.RS_Ratio(df=data0[['time','Close','closeIndex']])

    data['0700.hk/HSI']=rs

    return data

if __name__ == '__main__':
    data=getData()

    showRRG_M(**data)