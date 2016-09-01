import oandaData as od

def updateInstrument():
    insts=od.readInsts()
    errorlog=open('error_instrument.txt','w')
    for i in insts:
        print(i)
        error=od.update(instrument=i)
        if len(error)>0:
            errorlog.write('%s:' % i)
            for e in error:
                errorlog.write(' %s,' % e)
            errorlog.write('\n')



if __name__ == '__main__':
    updateInstrument()