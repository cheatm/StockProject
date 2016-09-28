import pandas
import numpy as np
import talib

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

class Order():

        def __init__(self,ticket,code,openPrice,lots,lever,time,stoplost=0,takeprofit=0,comment=None):

            self.code=code
            self.openPrice=openPrice
            self.lots=lots
            self.stoplost=stoplost
            self.takeprofit=takeprofit
            self.ticket=ticket
            self.deposit=abs(openPrice*lots/lever)
            self.openTime=time
            self.comment=comment

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

            self.closePrice=price
            self.profit=profit

class Account():

    orders=[]
    ordersHistory=[]
    Time=0
    capital=[]

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
        self.initCash=initCash
        self.nextTicket=0
        pass

    def closeOrder(self,price,order):
        '''

        :param price:
        :param order:
        :return:
        '''
        order.close(price,self.Time)
        self.cash=self.cash+order.profit+order.deposit
        self.ordersHistory.append(order)
        self.orders.remove(order)

    def openOrder(self,code,price,lots,stoplost=0,takeprofit=0,ticket=None,comment=None):
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

        order=Order(ticket,code,price,lots,self.lever,self.Time,stoplost,takeprofit,comment)
        self.cash=self.cash-order.deposit
        self.orders.append(order)

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
        attrs=['ticket','code','openTime','closeTime','openPrice','closePrice','lots','stoplost','takeprofit','deposit','profit']
        orders=[]
        for o in self.ordersHistory:
            order=[]
            for a in attrs:
                order.append(getattr(o,a))
            orders.append(order)

        return pandas.DataFrame(orders,columns=attrs)

    def marginLog(self):
        log=[self.initCash]
        for o in self.ordersHistory:
            log.append(log[-1]+o.profit)

        return(log)

    def refresh(self,time,price):
        self.Time=time

        for o in self.orders:
            o.refresh(price,self)

        capital=self.cash
        for o in self.orders:
            capital=capital+o.profit+o.deposit

        self.capital.append([time,capital])

    def findOrder(self,value,searchBy='comment',mode='orders'):
        for o in getattr(self,mode):
            if getattr(o,searchBy)==value:
                return o

    def findOrders(self,mode='orders',**how):
        out=[]
        for o in getattr(self,mode):
            isOrder=True
            for k in how.keys():
                if getattr(o,k)!=how[k]:
                    isOrder=False
                    break
            if isOrder:
                out.append(o)

        return out

class System():

    data={}
    params={}
    funcparam={}
    selectorlist=[]

    def __init__(self,default='close',account=Account()):

        self.acc=account
        self.setCustomSelector()
        self._set_selector()
        self._set_funcparam()
        self.default=default
        self.init()

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

    def makeIndicator(self,indicator,time,*values,**params):
        value=[]
        for v in values:
            if isinstance(v,np.ndarray):
                value.append(v)
            else:
                value.append(np.array(v))

        ind=getattr(talib,indicator)(*value,**params)
        data={'time':time}
        if isinstance(ind,tuple):
            count=0
            for i in ind:
                data[count]=i
                count+=1
        else:
            data[0]=ind
        ind=pandas.DataFrame(data).dropna()

        return ind

    def refreshAccount(self,time,price):
        self.acc.Time=time
        for i in range(0,len(self.acc.orders)):
            for k in self.data.keys():
                if self.acc.orders[i].code==k:
                    pass

    def runSelector(self,start=None,end=None,**kwds):
        '''

        :param kwds:
            functions: filter='', entry='', exit='', stoplost='', takeprofit='', ...
            params: fast=10, slow=20, ...

        :return:
        '''

        for k in kwds.keys():
            if k not in self.selectorlist:
                setattr(self,k,kwds[k])

        self.makeIndicators()

        Filter=getattr(self,kwds['Filter'])
        Entry=getattr(self,kwds['Entry'])
        Exit=getattr(self,kwds['Exit'])
        StopLost=getattr(self,kwds['StopLost'],0)
        TakeProfit=getattr(self,kwds['TakeProfit'],0)

        basicData=self.data[self.code]
        for i in basicData.index[start:end]:
            price=self.getPrice(self.code,self.default)
            self.time=basicData.get_value(i,'time')
            self._set_Time_Data()
            self.acc.refresh(self.time,price)

            for o in self.acc.orders:
                if Exit()*o.losts>0:
                    self.acc.closeOrder(price,o)

            direct=Filter()
            if direct==0:
                continue

            if Entry()*direct>0:
                self.acc.openOrder(self.code,price,abs(Entry())*direct,StopLost(),TakeProfit())

    def _set_Time_Data(self):
        self.timeData={}
        for name in self.data.keys():
            data=self.data[name]
            if isinstance(data,pandas.DataFrame):
                data=data[data['time']<=self.time]
                data.index=reversed(np.arange(0,data.index.size))
                self.timeData[name]=data

    def simpleStrategy(self):
        pass

    def runSimple(self,start=None,end=None,**kwds):
        for k in kwds.keys():
            if k not in self.selectorlist:
                setattr(self,k,kwds[k])

        self.makeIndicators()

        basicData=self.data[self.code]

        for i in basicData.index[start:end]:
            self.time=basicData.get_value(i,'time')
            self._set_Time_Data()
            self.acc.refresh(self.time,self.getPrice(self.code,'closeBid')*10000)
            self.simpleStrategy()

    def optimalizeSimple(self,**params):
        paramsTree=STree('params',**params)

        paramsComb=paramsTree.showAllCombination()

        for pc in paramsComb:
            self.runSimple(**pc)

    def optimalize(self,start=None,end=None,params=None,funcparam=None,selector=None):
        params=self.params if params is None else params
        funcparam=self.funcparam if funcparam is None else funcparam

        if selector is None:
            selector={}
            for select in self.selectorlist:
                selector[select]=list(getattr(self,select).keys())

        sTree=STree('tree',**selector)
        sTree.createParamBranch(params,funcparam)

        sa=sTree.showAllCombination()

        for comb in sa:
            self.runSelector(start,end,**comb)

    def init(self):
        pass

    def setCustomSelector(self):
        pass

    def makeIndicators(self):
        pass

if __name__ == '__main__':

    pass




