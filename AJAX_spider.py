import requests,re
import pandas,json
import  time

def nfpFromWallstreet():
    url='https://api-markets.wallstreetcn.com//v1/calendar_item_values.json?id=402361'
    page=requests.get(url)
    data=json.loads(page.text)
    # pattern1='''<div class="finance-calendar-container finance-data-container">(.*?)</div>'''

    # nfp=re.findall(pattern1,page.text,re.S)

    return (data['results'][0])

def nfpFromInvesting():
    url='http://www.investing.com/economic-calendar/nonfarm-payrolls-227'

    page=requests.get(url)

    pattern1='''eventHistoryTable227.*?<tbody>(.*?)</tbody>'''
    pattern2='''event_timestamp="(.*?) .*?".*?<td class="noWrap">.*?>(.*?)</span>.*?<td class="noWrap">(.*?)</td>.*?noWrap">(.*?)</td>'''

    tbody=re.findall(pattern1,page.text,re.S)
    nfp=re.findall(pattern2,tbody[0],re.S)

    nfp=pandas.DataFrame(nfp,columns=['Date','Actual','Forecast','Previous'])
    return (nfp)

def nfp_compare():
    def catchNumber(s):
        out=0
        for n in s:
            if n.isdigit():
                out=out*10+(int)(n)

        return out

    consequence={}

    investing=nfpFromInvesting()
    wallstreet=nfpFromWallstreet()

    if wallstreet['actual'] is not '':
        wsout=catchNumber(wallstreet['actual'])-catchNumber(wallstreet['forecast'])
        # print('WallStreet : %s' % wsout)
        consequence['WallStreet']=wsout
    # else:
        # print('WallStreet : No Actual Data')

    # print(investing)
    if 'nbsp' not in investing.get_value(0,'Actual'):
        investingOut=catchNumber(investing.get_value(0,'Actual'))-catchNumber(investing.get_value(0,'Forecast'))
        # print("Investing : %s" % investingOut)
        consequence['Investing']=investingOut
    # else:
        # print('Investing : No Actual Data')

    return consequence


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
    # nfpFromInvesting()
    # print(nfpFromWallstreet())
    con=nfp_compare()
    consequence=[]

    while(len(consequence)<2):
        if len(consequence)==0:
            print("No actual data at %s" % time.strftime('%H:%M:%S',time.localtime()))

        # if len(consequence)==1:
        #     print(consequence[0])

        consequence=[]
        time.sleep(10)
        con=nfp_compare()
        for k in con.keys():
            out="%s : %s at %s" % (k,con[k],time.strftime('%H:%M:%S',time.localtime()))
            consequence.append(out)
            print(out)


    # print(consequence)
