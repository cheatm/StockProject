import oandaData
import pandas


class Account():


    def __init__(self,initCash=1000000):
        self.holding=pandas.DataFrame(data=[['cash',0,0,initCash]],columns=['code','lots','price','value'])

    def buy(self,code,lots,price):
        self.holding.set_value(0,'value',self.holding.get_value(0,'value')-lots*price)
        self.holding=self.holding.append(
            pandas.DataFrame(data=[[code,lots,price,lots*price]],
            index=[self.holding.index.tolist()[-1]+1],
            columns=['code','lots','price','value'])
        )

        pass

    def sell(self,code,lots,price):
        pass


if __name__ == '__main__':
    acc=Account()
    print(acc.holding)
    acc.buy('0700.hk',100,100)
    print(acc.holding)