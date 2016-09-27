import oandaData
import pandas
import indicator
import time
import numpy as np

class STree():

    leaves={}

    def __init__(self,name,type='0',*strategies,**typeStrategies):
        '''

        :param name: name of the tree
        :param strategies: list of strategies names:['entry1','entry2',...]
        :return:
        '''

        self.name=name
        self.type=type
        self.create(type,*strategies,**typeStrategies)

    def createParamBranch(self,params,funcParams,**need):
        inneedParam=need.copy()
        pa=params.copy()
        if self.name in funcParams.keys():
            for p in funcParams[self.name]:
                if p in params:
                    inneedParam[p]=params[p]
                    pa.pop(p)

        for name in self.leaves.keys():
            tree=self.leaves[name]
            if isinstance(tree,STree):
                tree.createParamBranch(pa,funcParams,**inneedParam)

        if len(self.leaves)==0:
            self.__init__(self.name,self.type,**inneedParam)

        pass

    def create(self,type,*strategies,**ts):
        leaves={}
        nextType= str(int(type)+1) if type.isdigit() else type

        if len(strategies)>1:
            for s in strategies[0]:
                leaves[s] = STree(s,nextType,*strategies[1:],**ts)

        elif len(strategies)==1:
            for s in strategies[0]:
                leaves[s]= STree(s,nextType,**ts)

        else:
            if len(ts)>0:
                t,leave=ts.popitem()
                for s in leave:
                    leaves[s]=STree(s,t,**ts)


        self.leaves=leaves.copy()

    def showBranchesDict(self,tree,**parentDict):
        thisDict=parentDict.copy()
        thisDict[tree.type]=tree.name
        thisList=[]

        for name in tree.leaves.keys():
            if isinstance(tree.leaves[name],STree):

                next=tree.showBranchesDict(tree.leaves[name],**thisDict)
                thisList.extend(next)
            else :
                thisList.append(thisDict)

        if len(tree.leaves)==0:
            thisList.append(thisDict)

        return thisList

    def showBranches(self,tree,*nameList):
        thisList=[]
        for name in tree.leaves.keys():
            if isinstance(tree.leaves[name],STree):
                leaveList=list(nameList).copy()
                leaveList.append(name)

                thisList.extend(tree.showBranches(tree.leaves[name],*leaveList))
            else :
                thisList.append(nameList)
        if len(tree.leaves)<1:
            thisList.append(nameList)

        return thisList

    def showAllCombination(self):
        combList=[]
        for name in self.leaves.keys():
            tree=self.leaves[name]
            combList.extend(self.showBranchesDict(tree))
        return combList

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

    params={}
    funcparam={}
    selectorlist=[]

    def __init__(self,entry=None,exit=None,account=Account()):

        self.acc=account
        self._set_custom_selector()
        self._set_selector()
        self._set_funcparam()

    def pop__(self,x):
        return '__' not in x

    def _set_selector(self):
        if self.selectorlist.__len__()==0:
            self.selectorlist=['Filter','Entry','Exit']

        selfAttrs=list(filter(self.pop__,self.__dir__()))

        for s in self.selectorlist:
            if not hasattr(self,s):
                setattr(self,s,{})
            sdict=getattr(self,s)

            for a in selfAttrs:
                if s in a and s != a :
                    attr=getattr(self,a)
                    if isinstance(getattr(self,a),type(self.__init__)):
                        sdict[a]=attr

    def _set_custom_selector(self):
        pass

    def _set_funcparam(self):
        selfAttrs=list(filter(self.pop__,self.__dir__()))

        for s in self.selectorlist:
            selector=getattr(self,s)
            for name in selector.keys():
                if '%s_param' % name in selfAttrs:
                    self.funcparam[name]=getattr(self,'%s_param' % name)

    def getPrice(self,name,column,shift=0):
        data=self.timeData[name]
        return data.get_value(shift,column) if len(data.index)>shift else 0

    def getPrices(self,name,array,*columns):
        data=self.timeData[name]
        return data.loc[array,columns] if len(data.index)>max(array) else 0

    def setParams(self,**kwds):
        for k in kwds.keys():
            self.params[k]=kwds[k]

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

    def runSelector(self,**kwds):
        '''

        :param kwds:
            functions: filter='', entry='', exit='', stoplost='', takeprofit='', ...
            params: fast=10, slow=20, ...

        :return:
        '''

        for k in kwds.keys():
            if k not in self.selectorlist:
                setattr(self,k,kwds[k])

        Filter=getattr(self,kwds['Filter'])
        Entry=getattr(self,kwds['Entry'])
        Exit=getattr(self,kwds['Exit'])

        basicData=self.data[self.code]
        for i in basicData.index[10:20]:
            self.time=basicData.get_value(i,'time')
            self._set_Time_Data()

            print(self.getPrices(self.code,np.arange(0,10),'time','closeBid','closeAsk'))
            self.refreshAccount(self.time,basicData.loc[i,basicData.columns[1:]])

            for o in self.acc.orders:
                pass

            direct=Filter()
            if direct==0:
                continue

            if Entry()==direct:
                self.entryOrder(direct)

    def entryOrder(self,direct):

        pass

    def exitOrder(self,direct,ticket):
        pass

    def _set_Time_Data(self):
        self.timeData={}
        for name in self.data.keys():
            data=self.data[name]
            if isinstance(data,pandas.DataFrame):
                data=data[data['time']<=self.time]
                data.index=reversed(data.index)
                self.timeData[name]=data



    def optimalize(self,params=None,funcparam=None,selector=None):
        params=self.params if params is None else params
        funcparam=self.funcparam if funcparam is None else funcparam

        if selector is None:
            selector={}
            for select in self.selectorlist:
                selector[select]=list(getattr(self,select).keys())

        sTree=STree('tree',**selector)
        sTree.createParamBranch(params,funcparam)

        sa=sTree.showAllCombination()
        print(pandas.DataFrame(sa))


class MySys(System):

    fast=6
    slow=12
    signal=9
    selector = ['Filter','Entry','Exit']

    def _set_custom_selector(self):
        self.Entry={'macdin':self.macdin}
        self.Exit={'macdout':self.macdout}

    def Entry_1(self):
        print('fast',self.fast)
        return 0

    def Entry_2(self):
        print('2_slow:',self.slow)
        return  0

    def Exit_1(self):
        print('exit')
        return 0

    def Filter1(self):
        return 0

    macdin_param=['fast','slow','signal']
    def macdin(self):
        print('macd_in')
        return 0

    macdout_param=['fast','slow','signal']
    def macdout(self):
        print('macd_out')

        return 0

def def3(cls):
    start=time.time()
    t=cls.time
    ma=cls.getind('MACD','EUR_USD',shift=list(range(0,5)),time=t)
    print(time.time()-start)
    if isinstance(ma,int):
        return 0

    def param():
        return ['a','b','c']

    return 0
def3.__setattr__('param',['a','b','c'])

def accountTest():
    acc=Account()
    acc.openOrder('EUR_USD',10000,1,9990,10300)
    acc.openOrder('EUR_USD',10000,-1,10090,9890)

    acc.closeOrder(9990,pos=1)

def systemTest():
    data=oandaData.read_sql('D','EUR_USD')
    COT=oandaData.read_sql('COT','EUR_USD')

    system=MySys()
    system.importData('EUR_USD',data,True)
    system.importData('COT',COT)
    system.setParams(fast=[6,7,8,9,10],
                     slow=[12,14,16],
                     signal=[9,10,11])

    system.runSelector(Entry='Entry_1',Filter='Filter1',Exit='macdin')


if __name__ == '__main__':

    systemTest()
    pass




