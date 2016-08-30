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

class System():

    entry={}

    def __init__(self,entry=None,account=Account()):

        self.acc=account
        self.setEntry(entry)

    def setEntry(self,entry):
        for k in entry.keys():
            self.entry[k]=entry[k]

        print(self.entry)

    def run(self):
        for e in self.entry:
            e()

def def1():
    print('def1')


if __name__ == '__main__':
    system=System()
    system.setEntry({'def1':def1})


    pass