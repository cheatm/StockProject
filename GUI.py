# __author__ = 'CaiMeng'
# GUI

import pandas
import matplotlib.pyplot as plt
import tushare as ts
import wx


class MyFrame(wx.Frame):
    def __init__(self,superior):
        #初始化
        wx.Frame.__init__(self,parent=superior,id=1,title='My_Frame',size=(600,400))


def getData():
    ts.set_token('21d74eb20a01e50e386d1f48946a18e781dec2d2861587564198836495a5ec03')
    print(ts.get_token())
    mkt=ts.Market()
    HSI=mkt.MktIdxd(ticker='HSI',field='tradeDate,openIndex,lowestIndex,highestIndex,closeIndex')
    print(HSI.closeIndex)

    # plt.plot(HSI.closeIndex)
    # print('plt.plot success')
    # plt.show()
    # print('plt.show success')

if __name__ == '__main__':
    # getData()
    app=wx.App()
    frame=MyFrame(None)
    frame.Show(True)
    app.MainLoop()