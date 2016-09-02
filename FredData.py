from fredapi import Fred
import pandas,time,sqlite3
from datetime import date,datetime
import indicator as ind

class myFred():
    savePath=open('ini/FredSavePath.txt').read()
    codeDict={
        'Real_GDP':'A191RL1Q225SBEA',
        'Initial_Claims':'IC4WSA',
        'Total_Nonfarm_Payrolls':'PAYEMS',
        'Civilian_Unemployment_Rate':'UNRATE',
        'Industrial_Production_Index': 'INDPRO'
    }
    speedList=['Initial_Claims','IC4WSA','Total_Nonfarm_Payrolls','PAYEMS',
               'Industrial_Production_Index', 'INDPRO']

    def __init__(self):
        self.fred=Fred(api_key='2c149bd5d320ce48476143f35aa2bf02')


    def getData(self,name=None,code=None,start=datetime(1999,1,1),end=None):
        if code is None:
            code=self.codeDict[name]

        data=self.fred.get_series(code,observation_start=start,observation_end=end)
        data=pandas.DataFrame({'Date':data.index.tolist(),'Value':data.tolist()})

        date=data['Date'].tolist()
        t=[]

        for d in date:
            try:
                t.append(d.timestamp())
            except Exception as e:
                t.append(None)
        data.insert(0,'time',t)


        return data.dropna()

    def saveMultiple(self,*namelist):

        if len(namelist)==0:
            namelist=self.codeDict.keys()
        con=sqlite3.connect('%s/%s.db' % (self.savePath,'FredData'))
        for k in self.codeDict.keys():
            print(k)
            data=self.getData(name=k)
            if k in self.speedList:
                data=self.rsi(self.Speed(data))


            self.save_sql(k,data.set_index('time').dropna(),con=con)
        con.close()

    def Speed(self,data):
        velocity=[0]
        acceleration=[0,0]
        value=data['Value'].tolist()

        former=value[0]
        for v in value[1:]:
            velocity.append(v-former)
            former=v

        former=velocity[1]
        for v in velocity[2:]:
            acceleration.append(v-former)
            former=v

        data.insert(2,'Velocity',velocity)
        data.insert(3,'Acceleration',acceleration)
        return data

    def rsi(self,data,column='Velocity',period=5):
        RSI=ind.RSI(data['time'],data[column],period)
        return data.merge(RSI,'outer','time')


    def save_sql(self,table,data,name=None,path=None,con=None,if_exists='replace'):
        close=False

        if path is None:
            path='%s/%s.db' % (self.savePath,name)

        if con is None:
            con=sqlite3.connect(path)
            close=True

        data.to_sql(table,con,if_exists=if_exists)

        if close:
            con.close()



if __name__ == '__main__':
    mf=myFred()
    mf.saveMultiple()