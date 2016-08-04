import requests,re
import pandas,json

def test():
    url='http://www.investing.com/economic-calendar/nonfarm-payrolls-227'

    page=requests.get(url)

    pattern1='''eventHistoryTable227.*?<tbody>(.*?)</tbody>'''
    pattern2='''event_timestamp="(.*?) .*?".*?<td class="noWrap">.*?>(.*?)</span>.*?<td class="noWrap">(.*?)</td>.*?noWrap">(.*?)</td>'''

    tbody=re.findall(pattern1,page.text,re.S)
    nfp=re.findall(pattern2,tbody[0],re.S)

    nfp=pandas.DataFrame(nfp,columns=['Date','Actual','Forecast','Previous'])
    print(nfp)

def postTest():
    url='http://www.investing.com/economic-calendar/more-history'

    formData={
        'eventID':'324133',
        'event_attr_ID':'227',
        'event_timestamp':'2016-03-04 13:30:00',
        'is_speech':'0'
    }

    headers={
        'Accept':'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Content-Length':'84',
        'Content-Type':'application/x-www-form-urlencoded',
        'Host':'www.investing.com',
        'Origin':'http://www.investing.com',
        'Proxy-Authorization':'Basic Y2hhbm5lbEByZWNoYXJnZS5oazpsb25nMTAxMw==',
        'Proxy-Connection':'keep-alive',
        'Referer':'http://www.investing.com/economic-calendar/nonfarm-payrolls-227',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'
    }

    page=requests.post(url,data=formData,headers=headers)

    print(page)

def scrpyTest():

    pass

if __name__ == '__main__':
    test()
