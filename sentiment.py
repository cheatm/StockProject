import oandaData as od
import indicator as ind
import pandas
from datetime import datetime

def showHPR_spr(*insts):
    if len(insts)==0:
        insts=od.readInsts()[0:5]

    hpr=[]
    for i in insts:
        data=od.read_sql('HPR',i)
        index=data.index.tolist()[-1]
        hpr.append(data.get_value(index,'short_position_ratio'))

    out=pandas.DataFrame([hpr],columns=insts)
    print('HPR:short_position_ratio')
    print(out)

def COTindex(*insts,n=14):
    if len(insts)==0:
        insts=od.readInsts()[0:5]

    out=None
    for i in insts:
        currents=i.split('_')
        column='-'
        if currents[0] is 'USD':
            column='s-l'
        else:
            column='l-s'

        data=od.read_sql('COT',i)
        sent=ind.sentiment(data.time,data[column],n)
        sent.columns=['time',i]
        if out is None:
            out=sent
        else:
            out=out.merge(sent,how='outer',on='time')

    date=[]
    for t in out.time:
        date.append(datetime.fromtimestamp(t).date())

    out.insert(1,'date',date)

    print(out.loc[out.index[-10]:])


if __name__ == '__main__':
    # showHPR_spr()
    COTindex()
    pass
