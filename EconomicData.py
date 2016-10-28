import re
import requests
import pandas
import time
import random


def getNonFarmPayroll():
    nfp=requests.get('https://www.oanda.com/forex-trading/analysis/economic-indicators/united-states/employment/non-farm-payroll')
    patternTable='''Date</th>
.*?Value</th>
.*?Previous</th>
.*?Change</th>
(.*?)</table>'''
    tableString= re.findall(patternTable,nfp.text,re.S)
    # print(tableString)
    patternData='''<tr>.*?<td>(.*?)</td>.*?<td>.*?>(.*?)</span>.*?<td>(.*?)</td>.*?<td>.*?>(.*?)&.*?</tr>'''
    nfpString= re.findall(patternData,str(tableString),re.S)
    nfp=pandas.DataFrame(data=nfpString,columns=['Date','Value','Previous','Change'])
    return nfp

def getYieldCurve():
    yc=requests.get('https://www.oanda.com/forex-trading/analysis/economic-indicators/united-states/rates/yield-curve')
    patternTable='''Date</th>
.*?Value</th>
.*?Previous</th>
.*?Change</th>
(.*?)</table>'''
    tableString= re.findall(patternTable,yc.text,re.S)
    patternData='''<tr>.*?<td>(.*?)</td>.*?<td>.*?>(.*?)</span>.*?<td>(.*?)</td>.*?<td>.*?>(.*?)&.*?</tr>'''
    ycString= re.findall(patternData,str(tableString),re.S)
    yc=pandas.DataFrame(data=ycString,columns=['Date','Value','Previous','Change'])
    return yc

def getEconomicCalendar():
    ec=requests.get('http://www.investing.com/economic-calendar/')
    pattern='''data-event-datetime="(.*?)">.*?</span>(.*?)</td>.*?bull(.*?)".*?<a.*?>.*?\t...(.*?)</a>.*?<td.*?>(.*?)</td>.*?<td.*?>(.*?)</td>.*?<span.*?>(.*?)</span>'''
    ecString=re.findall(pattern,ec.text,re.S)
    ec=pandas.DataFrame(data=ecString,columns=['Time','Cur.','Imp.','Event','Actual','Forecast','Previous'])

    return ec

def getUSInitialJoblessClaims():
    ijc=requests.get('http://www.investing.com/economic-calendar/initial-jobless-claims-294')
    pattern='''event_timestamp="(.*?)">.*?<span.*?>(.*?)</span></td>.*? <td.*?>(.*?)</td>.*? <td.*?>(.*?)</td>'''
    ijcString=re.findall(pattern,ijc.text,re.S)
    ijc=pandas.DataFrame(data=ijcString,columns=['Time','Actual','Forecast','Previous'])
    c='Actual'
    for i in ijc.index:
        print(i,ijc.get_value(i,c))

    return ijc

def getNonfarmPayrolls():
    url='http://www.investing.com/economic-calendar/nonfarm-payrolls-227'

    page=requests.get(url)

    pattern1='''eventHistoryTable227.*?<tbody>(.*?)</tbody>'''
    pattern2='''event_timestamp="(.*?) .*?".*?<td class="noWrap">.*?>(.*?)</span>.*?<td class="noWrap">(.*?)</td>.*?noWrap">(.*?)</td>'''

    tbody=re.findall(pattern1,page.text,re.S)
    nfp=re.findall(pattern2,tbody[0],re.S)

    nfp=pandas.DataFrame(nfp,columns=['Date','Actual','Forecast','Previous'])
    return (nfp)

def test1():
    out=[]
    for p in range(1,5):
        url='http://www.jikexueyuan.com/course/?pageNum=%s' % p
        page=requests.get(url)
        pattern='''<div class="lesson-infor".*?<a.*?">(.*?)</a>.*?<p.*?>(.*?)</p>.*?<em>(.*?)</em>.*?<em class="learn-number">(.*?)</em>'''
        out.extend(re.findall(pattern,page.text.strip(),re.S))
        print('finish page %s' % p)
    data=pandas.DataFrame(data=out,columns=['课程名称','课程简介','课时','学习人数'])

    return data

def getYahooData(proxy=None,html=None):
    url='https://hk.finance.yahoo.com/advances'
    # 修改header 伪装成浏览器
    '''
    RequestHeaders:
    accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    accept-encoding:gzip, deflate, sdch, br
    accept-language:zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4
    cache-control:max-age=0
    cookie:B=a7083ndboshfj&b=3&s=om; ypcdb=2425aba8313c8113f91b3a94606c7070; PRF=&t=^HSCE+27787.HK
    upgrade-insecure-requests:1
    user-agent:Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36
    '''

    UAlist=[
        {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'},
        {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36 OPR/39.0.2256.48'},
        {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586'},
        {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0'},
        {'user-agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36'}
    ]

    # header=UAlist[random.randint(0,3)]
    header=UAlist[2]
    print(header)

    # proxy={'http': 'http://182.38.24.70:8118'}

    page=requests.get(url,headers=header,timeout=5000)
    bodyPattern='''<th>HK</th><th>NASDAQ</th>.*?<tbody>(.*?)</tbody>'''
    tbody=re.search(bodyPattern,page.text,re.S)

    tbody=tbody.string.strip('\n')
    dataPattern='''<td align="right">(.*?)</td><td align="right">(.*?)</td>'''
    data=re.findall(dataPattern,tbody,re.S)
    index=['Raise','Fall','Unchange','All','NewHigh','NewLow','VolIncrease','VolDecrease','VolUnchange','VolTotal']
    # out=pandas.DataFrame(data=data,columns=['HK','NASDAQ'],index=index)
    print(data)

    def getNum(value):
        v=0
        for a in value:
            if a.isdigit():
                v=10*v+int(a)
            elif a is  ',':
                continue
            else:
                break
        return v

    HK,NASDAQ={},{}
    n=0
    for hk,nsdq in data:
        HK[index[n]]=getNum(hk)
        NASDAQ[index[n]]=getNum(nsdq)
        n+=1

    out={'HK':HK,'NASDAQ':NASDAQ}
    print (out)
    # for b in out.columns:
    #     for a in out.index:
    #         out.set_value(a,b,getNum((out.get_value(a,b))))

    # return out.T
    return out

def IPAddressSearcher():
    url="http://www.xicidaili.com/nn/1"
    User_Agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
    header = {}
    header['User-Agent'] = User_Agent
    pattern1='''<table id="ip_list">(.*?)</table>'''
    pattern2='''<tr class.*?<td class.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?href.*?</tr>'''

    page=requests.get(url,headers=header)


    addresses=re.findall(pattern1,page.text,re.S)
    addressList=re.findall(pattern2,addresses[0],re.S)

    # out=pandas.DataFrame(addressList)

    return(addressList)

def IpTest(addressList):
    proxys=[]
    for a in addressList:
        host="http://%s:%s" % a
        proxy={'http':host}
        try:
            res=requests.get("http://ip.chinaz.com/getip.aspx",proxies=proxy)
            proxys.append(proxy)
            print(res.text)
            if(len(proxys)>=10):
                return (proxys)
        except Exception as e:
            print(proxy)
            print(e)
            continue

        time.sleep(3)
    return (proxys)


if __name__ == '__main__':

    pass