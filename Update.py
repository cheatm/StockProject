import oandaData as od
import HKStock as hs
import threading,threadpool

insts=od.readInsts()

def updateInstrument():

    errorlog=open('error_instrument.txt','w')
    for i in insts:
        print(i)
        error=od.update(instrument=i)
        if len(error)>0:
            errorlog.write('%s:' % i)
            for e in error:
                errorlog.write(' %s,' % e)
            errorlog.write('\n')

def updateHoldings():

    pool=threadpool.ThreadPool(5)

    for i in insts[0:5]:
        pool.putRequest(threadpool.WorkRequest(od.updateCOT,[i]))
        pool.putRequest(threadpool.WorkRequest(od.updateHPR,[i]))

    pool.wait()

def updateHKStock():
    table_names=open('ini/HKStockList.txt').read().split(',')
    pool=threadpool.ThreadPool(5)
    for name in table_names:

        path='%s/%s.db' % (hs.savePath,name)
        print(path)
        workrequest=threadpool.WorkRequest(hs.updateStockData,[name])
        pool.putRequest(workrequest)

    pool.wait()


if __name__ == '__main__':
    updateInstrument()
    updateHoldings()
    updateHKStock()
    pass