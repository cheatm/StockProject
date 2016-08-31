import oandaData
import pandas
import indicator


class Account():

    class order():

        def __init__(self,ticket,code,openPrice,lots,lever,stoplost=0,takeprofit=0):

            self.code=code
            self.openPrice=openPrice
            self.lots=lots
            self.stoplost=stoplost
            self.takeprofit=takeprofit
            self.ticket=ticket
            self.deposit=abs(openPrice*lots/lever)

        def close(self,price,cls=None):

            self.closePrice=price
            self.profit=(self.closePrice-self.openPrice)*self.lots

        def refresh(self,price,cls):

            profit=(price-self.openPrice)*self.lots

            if profit>(self.takeprofit-self.openPrice)*self.lots:
                cls.closeOrder(ticket=self.ticket,price=self.takeprofit)

                return

            if profit<(self.stoplost-self.openPrice)*self.lots:
                cls.closeOrder(ticket=self.ticket,price=self.stoplost)

                return

            self.close=price
            self.profit=profit


    orders=[]
    ordersHistory=[]

    def __init__(self,initCash=1000000,lever=1):
        '''

        :param initCash: initial cash
        :param lever: >1
        :return:

        How to use:
            # create an account:
            acc=Account()


        '''


        self.lever=lever
        self.cash=initCash
        self.nextTicket=0
        pass

    def closeOrder(self,price,ticket=None,pos=0):
        '''
        close an order by position or by ticket

        :param price: necessary
        :param ticket: close order by orderticket
        :param pos:
            close order by the position of order on the orderlist:
                0: earliest opentime
                -1: latest opentime
        :return:
        '''
        if ticket is not None:
            for i in range(0,len(self.orders)):
                if self.orders[i].ticket==ticket:
                    self.orders[i].close(price)
                    self.cash=self.cash+self.orders[i].profit+self.orders[i].deposit
                    self.ordersHistory.append(self.orders[i])
                    self.orders.pop(i)
                    return

        self.orders[pos].close(price)
        self.cash=self.cash+self.orders[pos].profit+self.orders[pos].deposit
        self.ordersHistory.append(self.orders[pos])
        self.orders.pop(pos)

    def openOrder(self,code,price,lots,stoplost=0,takeprofit=0,ticket=None):
        '''
        open an order
        :param price:
        :param lots:
        :param stoplost:
        :param takeprofit:
        :param ticket:
        :return:
        '''
        if ticket is None:
            ticket=self.nextTicket

        order=self.order(ticket,code,price,lots,self.lever,stoplost,takeprofit)
        self.orders.append(order)
        self.cash=self.cash-order.deposit

        self.nextTicket=ticket+1



    def refreshOrders(self,price):
        for o in self.orders.copy():

            o.refresh(price,self)

    def getOrders(self):
        attrs=['ticket','code','openPrice','lots','stoplost','takeprofit','deposit']
        orders=[]
        for  o in self.orders:
            order=[]
            for a in attrs:
                order.append(getattr(o,a))
            orders.append(order)

        return pandas.DataFrame(orders,columns=attrs)

    def getHistoryOrders(self):
        attrs=['ticket','code','openPrice','closePrice','lots','stoplost','takeprofit','deposit']
        orders=[]
        for  o in self.ordersHistory:
            order=[]
            for a in attrs:
                order.append(getattr(o,a))
            orders.append(order)

        return pandas.DataFrame(orders,columns=attrs)


class System():

    data={}
    Entry={}
    Exit={}

    def __init__(self,entry=None,exit=None,account=Account()):

        self.acc=account
        self.setEntry(entry)
        self.setExit(exit)

    def setEntry(self,entry):
        if entry is not None:
            for k in entry.keys():
                self.Entry[k]=entry[k]

    def setExit(self,exit):
        if exit is not None:
            for k in exit.keys():
                self.Exit[k]=exit[k]

    # def setStoplost(self,stoplost):

    def importData(self,name,data):
        self.data[name]=data

    def getind(self,name,code,shift=0,out=None,time=None,input=['time','closeBid'],**kwargs):
        '''
        :param name: name of indicator which can be find in indicator.py
        :param code: code of data which has already been input into self.data
        :param shift: int or list[int]
        :param out: int or str
        :param input: list[str]
        :param kwargs: params for the indicator to be used

        :return:
            if out is None:
                return indicator with all columns : DataFrame
            else:
                if shift is int:
                    return single value with specific shift and column : float
                elif shift is list[int]:
                    return indicator of specific column : Series

        '''

        if time is None:
            time=self.time
        In=[]
        symbol=self.data[code]
        symbol=symbol[symbol['time']<=time]
        for i in input:
            In.append(symbol[i])

        ind=getattr(indicator,name)(*In,**kwargs)

        if isinstance(shift,list):
            for s in range(0,len(shift)):
                shift[s]=ind.index.tolist()[-shift[s]-1]
        else:
            shift=ind.index.tolist()[-shift-1]

        if out is not None:
            if isinstance(out,int):
                return ind.loc[shift][ind.columns[out]]

            if isinstance(out,str):
                return ind.loc[shift][out]

        return ind.loc[shift]

    def run(self):
        for k in self.Entry.keys():
            func=self.Entry[k]
            func(self)


def def3(cls):
    t=cls.data['EUR_USD'].get_value(90,'time')
    ma=cls.getind('MACD','EUR_USD',shift=[0,1,2,3,4],time=t)


    print(ma)


def accountTest():
    acc=Account()
    acc.openOrder('EUR_USD',10000,1,9990,10300)
    acc.openOrder('EUR_USD',10000,-1,10090,9890)


    acc.closeOrder(9990,pos=1)
    acc.refreshOrders(10400)

def systemTest():
    data=oandaData.read_sql('D','EUR_USD')

    system=System()
    system.importData('EUR_USD',data)
    system.setEntry({'def3':def3})
    system.run()


if __name__ == '__main__':
    systemTest()


