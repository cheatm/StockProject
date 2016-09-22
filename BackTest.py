import oandaData
import pandas
import indicator
import time


class Account():

    class order():

        def __init__(self,ticket,code,openPrice,lots,lever,time,stoplost=0,takeprofit=0):

            self.code=code
            self.openPrice=openPrice
            self.lots=lots
            self.stoplost=stoplost
            self.takeprofit=takeprofit
            self.ticket=ticket
            self.deposit=abs(openPrice*lots/lever)
            self.openTime=time

        def close(self,price,time,cls=None):
            self.closeTime=time
            self.closePrice=price
            self.profit=(self.closePrice-self.openPrice)*self.lots


        def refresh(self,price,cls):

            profit=(price-self.openPrice)*self.lots

            if self.takeprofit != 0:
                if profit>(self.takeprofit-self.openPrice)*self.lots:
                    cls.closeOrder(ticket=self.ticket,price=self.takeprofit)

                    return

            if self.stoplost != 0:
                if profit<(self.stoplost-self.openPrice)*self.lots:
                    cls.closeOrder(ticket=self.ticket,price=self.stoplost)

                    return

            self.close=price
            self.profit=profit

    orders=[]
    ordersHistory=[]
    Time=0

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
                    self.orders[i].close(price,self.Time)
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

        order=self.order(ticket,code,price,lots,self.lever,self.Time,stoplost,takeprofit)
        self.orders.append(order)
        self.cash=self.cash-order.deposit

        self.nextTicket=ticket+1

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

    param={}
    params={}
    funcparam={}

    def __init__(self,entry=None,exit=None,account=Account()):

        self.acc=account
        self.setEntry(entry)
        self.setExit(exit)

    def setParams(self,**kwds):
        for k in kwds.keys():
            self.params[k]=kwds[k]

        print(self.params)

    def setEntry(self,entry,param=None):
        if entry is not None:
            for k in entry.keys():
                self.Entry[k]=entry[k]

        if param is not None:
            for k in param.keys():
                self.funcparam[k]=param[k]
                for p in param[k]:
                    if p not in self.params:
                        self.params[p]=[]

    def entryOrder(self,code,lots,direction,k):
        func=self.Entry[k]
        f=func(self)
        if f != direction:
            return 0

        if direction==1:
            price=self.data[self.code]['closeAsk']
            self.acc.openOrder(code,price,lots)
        elif direction==-1:
            price=self.data[self.code]['closeBid']
            self.acc.openOrder(code,price,-lots)


    def setExit(self,exit,param=None):
        if exit is not None:
            for k in exit.keys():
                self.Exit[k]=exit[k]
        if param is not None:
            for k in param.keys():
                self.funcparam[k]=param[k]
                for p in param[k]:
                    if p not in self.params:
                        self.params[p]=[]

    def exitOrder(self,order):
        for k in self.Exit.keys():
            func=self.Exit[k]
            f=func(self)
            if f==-1:
                price=self.data[self.code]['closeAsk']
                if order.lots<0:
                    self.acc.closeOrder(ticket=order.ticket,price=price)
            elif f==1:
                price=self.data[self.code]['closeBid']
                if order.lots>0:
                    self.acc.closeOrder(ticket=order.ticket,price=price)

    def importData(self,name,data,maincode=False):
        if maincode:
            self.code=name
        self.data[name]=data

    def getind(self,name,code,shift=None,time=None,input=['time','closeBid'],**kwargs):
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
        In=[]
        symbol=self.data[code]
        shiftcopy=shift.copy() if isinstance(shift,list) else shift

        if time is not None:
            symbol=symbol[symbol['time']<=time]

        for i in input:
            In.append(symbol[i])

        ind=getattr(indicator,name)(*In,**kwargs)

        if shift is None:
            return ind

        if isinstance(shift,list):
            if shift[-1]+1>len(ind.index):
                return 0

            for s in range(0,len(shift)):
                shift[s]=ind.index.tolist()[-shift[s]-1]

            ind=ind.loc[shift]
            ind.index=shiftcopy
        else:
            if len(ind.index)<1:
                return 0
            shift=ind.index.tolist()[-shift-1]

            ind=ind.loc[shift]

        return ind

    def refreshAccount(self,time,price):
        self.acc.Time=time
        for i in range(0,len(self.acc.orders)):
            for k in self.data.keys():
                if self.acc.orders[i].code==k:
                    pass


    def run(self,**kwds):
        '''

        :param kwds:
            filter='', entry='', exit='', stoplost='', takeprofit='',
            param={'a':... ,'b':...}

        :return:
        '''

        basicData=self.data[self.code]
        for i in basicData.index:
            self.time=basicData.get_value(i,'time')
            self.refreshAccount(self.time,basicData.loc[i,basicData.columns[1:]])


            self.entryOrder(self.code,lots=100,direction=1,k='def3')

            for o in self.acc.orders:

                self.exitOrder(o)

    def optimalize(self):
        param={'para':{},'func':{}}
        paramList=[]
        # for en in self.Entry.keys():
        #     for ex in self.Exit.keys():
        #         param['func'][ex]=self.Exit[ex]
        #         param['func'][en]=self.Entry[en]
        #         paramList.append(param)
        #         param={'para':{},'func':{}}

        print(paramList)


        pass




def def3(cls):
    start=time.time()
    t=cls.time
    ma=cls.getind('MACD','EUR_USD',shift=list(range(0,5)),time=t)
    print(time.time()-start)
    if isinstance(ma,int):

        return 0

    # print(ma.get_value(0,'hist')>ma.get_value(1,'hist'))

    def param():
        return ['a','b','c']

    return 0
def3.__setattr__('param',['a','b','c'])

def exit1(cls):
    return 0

def entry2(cls):
    return 0

def accountTest():
    acc=Account()
    acc.openOrder('EUR_USD',10000,1,9990,10300)
    acc.openOrder('EUR_USD',10000,-1,10090,9890)

    acc.closeOrder(9990,pos=1)

def systemTest():
    data=oandaData.read_sql('D','EUR_USD')

    system=System()
    system.importData('EUR_USD',data,True)
    system.setParams(a=[1,2,3,4],b=[3,4,5,6],f=[1,2,3,4,5,6],c=[5,6])
    system.setEntry({'def3':def3,'entry2':entry2},
                    {'def3':['a','b','c'],'entry2':['f','b']})
    system.setExit({'exit1':exit1},{'exit1':['a','f']})
    system.optimalize()
    # system.run()
    # print(system.getind('MACD','EUR_USD'))
    print(system.params)
    print(system.funcparam)

class STree():

    leaves={}

    def __init__(self,name,type,*strategies):
        '''

        :param name: name of the tree
        :param strategies: list of strategies names:['entry1','entry2',...]
        :return:
        '''

        self.name=name
        self.type=type[0]
        self.create(type,*strategies)

    def create(self,type,*strategies):
        leaves={}

        if len(strategies)>1:
            for s in strategies[0]:
                leaves[s] = STree(s,type[1:],*strategies[1:])

        elif len(strategies)==1:
            for s in strategies[0]:
                leaves[s]= STree(s,[None])

        self.leaves=leaves.copy()
        # print(self.name,self.leaves)

    def showBranches(self,tree,*nameList):
        thisList=[]
        for name in tree.leaves.keys():
            if isinstance(tree.leaves[name],STree):
                leaveList=list(nameList).copy()
                leaveList.append(name)

                thisList.extend(tree.showBranches(tree.leaves[name],*leaveList))
            else :
                thisList.append(nameList)
                print(thisList)
        if len(tree.leaves)<1:
            thisList.append(nameList)

        return thisList

    def showAllCombination(self,):
        return pandas.DataFrame(self.showBranches(self))



if __name__ == '__main__':
    # systemTest()

    # def3.__setattr__('param',['a','b','c'])
    # print(def3.param)
    param={'a':[1,2,3],'b':[2,3,4],'c':[6,7]}

    sTree=STree('test',['Filter','Entry','Exit','StopLost','TakeProfit'],
                ['filter1','filter2','filter3'],['entry1','entry2','entry3'],['exit1','exit2','exit3'],['sl1','sl2'],['tp1','tp2'])

    print(sTree.showAllCombination())