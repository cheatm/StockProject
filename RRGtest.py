from PyQtTest import RRG_M
from PyQt4 import QtGui
import sys
import oandaData,indicator

def showRRG_M(**data):
    app=QtGui.QApplication(sys.argv)
    rrg=RRG_M()

    # print(data)
    for k in data.keys():

        rrg.importPrice(k,data[k]['time'],data[k]['closeBid'])


    rrg.show()
    sys.exit(app.exec_())

def getData():
    insts=oandaData.readInsts()
    data={}
    for i in insts[0:5]:
        data[i]=oandaData.read_sql('D',i)


    return data

if __name__ == '__main__':
    data=getData()


    showRRG_M(**data)