from PyQtTest import RRG_M
from PyQt4 import QtGui
import sys
import oandaData,indicator,HKStock

def showRRG_M(**data):
    app=QtGui.QApplication(sys.argv)
    rrg=RRG_M()

    # print(data)
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
    data2=HKStock.readStockData('Day','0002.hk')
    length2=data2.index.tolist()
    data2=data2.loc[length2[-15]:]
    data1=HKStock.readStockData('Day','0001.hk')
    length1=data1.index.tolist()
    data1=data1.loc[length1[-15]:]

    rs=indicator.RS_Ratio(data1.time.tolist(),data1.Close,data2.Close)
    print(rs)
    data['0001.hk/0002.hk']=rs

    return data



if __name__ == '__main__':
    data=getData()
    print(data)

    showRRG_M(**data)