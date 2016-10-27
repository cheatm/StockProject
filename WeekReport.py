import sentiment
import pymongo
import numpy as np
import math


def risk(values,direction):
        if direction>0:
            return (values[-1]/max(values))*100
        else:
            return values[-1]/min(values)*100

def RS_TS(data):

    numerator=math.log10(data[0]/data[-1])

    A=[]
    pre=data[0]
    for d in data[1:]:
        A.append(
            math.log10(pre/d)
        )
        pre=d

    denominator=np.std(A)

    return numerator/denominator if denominator!=0 else 0

def Noise_formula(data):
    up=abs(data[0]-data[-1])

    pre=data[0]
    Sum=0
    for p in data[1:]:
        Sum+=abs(p-pre)
        pre=p

    return up/Sum

def createReport(client,symbol):
    '''

    :param client:数据库client对象
    :param symbol: 品种
    :return: report{}
    '''

    # 创建report字典
    report={}

    # 表名：symbol.COT
    colName='%s.COT' % symbol
    # 按时间倒序获取'l-s'
    l_s=client.Oanda[colName].find(projection=['date','l-s'],sort=[('time',-1)])
    print(l_s[0])
    # 数据写入report
    report['COT']=l_s[0]['l-s']

    # 创建列表，count为周期
    lsList,count=[],100
    # 将最后count个l-s数据插入列表
    for ls in l_s[:count]:
        # 由于l-s是倒序 lsList在risk计算时要求正序 所以从头插入
        lsList.insert(0,ls['l-s'])
    print (lsList)
    # COt>0 方向为1 反之为-1
    direction=1 if report['COT']>0 else -1
    # 计算cot_risk 将数据格式化为最多2位小数的浮点数 插入report
    cr='%.2f' % risk(lsList,direction)
    report['COT_O']=cr
    print (cr)

    # 以下与上面的操作一样
    colName='%s.HPR' % symbol
    hpr=client.Oanda[colName].find(projection=['datetime','position'],sort=[('time',-1)])
    print(hpr[0])
    report['Sentiment']='+' if hpr[0]['position']>0 else '-'

    poslist,count=[],350

    for h in hpr[:count]:
        poslist.insert(0, h['position'])
    print(poslist)

    posrisk='%.2f' % risk(poslist,direction)
    report['position_risk']=posrisk

    # colName=symbol.D
    colName='%s.D' % symbol
    # 按时间倒序获取价格数据
    price=client.Oanda[colName].find(projection=['closeBid'],sort=[('time',-1)])

    priceList=[]
    # 取最近100个个closeBid
    for p in price[:100]:
        priceList.append(p['closeBid'])

    # 计算RS_TS
    report['RS_TS']=RS_TS(priceList)
    # 计算Noise_ER
    report['Noise_ER']=Noise_formula(priceList)

    report['symbol']=symbol

    return report


if __name__ == '__main__':

    # 连接数据库
    mClient=pymongo.MongoClient(host='localhost',port=10001)

    reportList=[]
    reportList.append(createReport(mClient,'EUR_USD'))
    reportList.append(createReport(mClient,'GBP_USD'))

    # '''保存report'''
    # mClient.Reports['report_20161027'].insert(reportList)

    # DataFrame显示
    print (reportList)
    import pandas
    reportFrame=pandas.DataFrame(reportList)
    reportFrame.set_index('symbol',inplace=True)
    print(reportFrame.T)
