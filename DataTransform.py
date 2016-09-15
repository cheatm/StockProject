import pandas
import time

def pandas_to_listSeries(pd,*columns):
    out=[]

    print(columns)
    for c in columns:
        out.append(pd[c].tolist())

    return (out)

def timeList_to_secondList(timeList,format):
    out=[]
    for t in timeList:
        timep=time.strptime(t,format)
        out.append(time.mktime(timep))
    return (out)