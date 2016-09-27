import oandaData as od
import HKStock as hs
import threadpool
import json,time

insts=od.readInsts()

def updateInstrument():
    global errors
    errors={}
    pool=threadpool.ThreadPool(5)
    def callBack(req,out):
        if len(out)>0:
            errors[req.kwds['instrument']]=out

    errorlog=open('error_instrument.txt','w')
    for i in insts:
        print(i)

        req=threadpool.WorkRequest(od.update,kwds={'instrument':i},callback=callBack)
        pool.putRequest(req)

    pool.wait()

    errorlog.write(json.dumps(errors))

    errorlog.close()

def errorReUpdate(path='error_instrument.txt'):
    file=open(path)
    text=file.read()

    error= json.loads(text) if text is not '' else {}
    file.close()

    if len(error)==0:
        print('No error occurs during last update')
        return

    time.sleep(2)

    errors={}
    for k in error.keys():
        out=od.update(*error[k],instrument=k)
        if len(out)>0:
            errors[k]=out
    file=open(path,'w')
    file.write(json.dumps(errors))
    file.close()

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
    # hs.updateIndex()
    errorReUpdate()

    pass