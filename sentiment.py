import oandaData as od
import indicator as ind
import pandas
from datetime import datetime
import numpy

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

def COTindex(*insts,n=200):
    if len(insts)==0:
        insts=od.readInsts()[0:5]

    out=None
    for i in insts:
        currents=i.split('_')
        column='-'
        if currents[0] == 'USD':
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
    # print('COT_sentiment')
    # print(out.loc[out.index[-10]:])
    return out.loc[out.index[-10]:]

def DirectionDegree(*insts,cotPeriod=100,hprPeriod=350):

    def risk(values,direction):
        if direction>0:
            return (values[-1]/max(values))*100
        else:
            return values[-1]/min(values)*100

    def riskStr(r):
        if r>60:
            return 'Riskiest'
        elif r>50:
            return 'Risky'
        elif r>40:
            return 'Safe'
        else:
            return 'Safest'



    insts=od.readInsts()[0:5] if len(insts)==0 else insts
    table=[]
    for i in insts:
        print(i)
        degree=[]
        degree.append(i) # Code

        column='l-s'
        cur=i.split('_')
        if cur[0]=='USD':
            column='s-l'
        cot=od.read_sql('COT',i)
        hpr=od.read_sql('HPR',i)
        cotnow=cot.get_value(cot.index[-1],column)
        if cotnow>0:
            degree.append('+') # COT
        else :
            degree.append('-') # COT

        position=hpr.get_value(hpr.index[-1],'position')
        if position>0:
            degree.append('+') # HPR_position
        else:
            degree.append('-') # HPR_position

        if degree[1] != degree[2]:
            degree.extend([0,0])
            table.append(degree) #
            continue

        direct=0
        if degree[1]=='+':
            direct=1
        else:
            direct=-1

        cr=risk(cot[cot.index[-cotPeriod]:][column].tolist(),direct)
        degree.append('%s%s(%.2f)' % (degree[1],riskStr(cr),cr)) # COT_Risk

        hr=risk(hpr[hpr.index[-hprPeriod]:]['position'].tolist(),direct)
        degree.append('%s%s(%.2f)' % (degree[1],riskStr(hr),hr)) # Position_Risk
        table.append(degree)


    out=pandas.DataFrame(table,columns=['Code','COT','HPR_position','COT_Risk','Position_Risk'])
    return out


if __name__ == '__main__':

    print (DirectionDegree())

    pass

