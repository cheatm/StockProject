from PyQt4 import QtCore,QtGui
import pandas,sys

class StockChart(QtGui.QMainWindow):

    Xalpha=0.2
    xMove=0

    # All data import into this class
    data=[]

    xRay=[]

    # default color
    colors=[
        QtGui.QColor('white'),
        QtGui.QColor('cyan'),
        QtGui.QColor('green'),
        QtGui.QColor('blue'),
        QtGui.QColor('gray'),
        QtGui.QColor('red'),
        QtGui.QColor('magenta'),
        QtGui.QColor('yellow')
    ]

    def __init__(self,parent=None,Xaxis=25,Yaxis=80):
        QtGui.QWidget.__init__(self,parent)

        self.initWidget()

        self.Xaxis=Xaxis
        self.Yaxis=Yaxis
        self.areaHeight=self.height()-self.Xaxis
        self.areaWidth=self.width()-self.Yaxis

        self.xCount=int(self.Xalpha*self.areaWidth)


        self.command={
            QtCore.Qt.Key_Down:self.down,
            QtCore.Qt.Key_Up:self.up,
            QtCore.Qt.Key_Left:self.left,
            QtCore.Qt.Key_Right:self.right
            }

    def keyPressEvent(self, event):

        if event.key() in self.command.keys():

            self.command[event.key()]()

    def left(self):
        if self.xMove+self.xCount<len(self.xRay):
            self.xMove=self.xMove+1
            self.repaint()

    def right(self):
        if self.xMove-1>=0:
            self.xMove=self.xMove-1
            self.repaint()
            print('r')


    def down(self):
        self.Xalpha*=0.8
        self.repaint()


    def up(self):
        self.Xalpha/=0.8
        self.repaint()

    def initWidget(self):

        screen=QtGui.QDesktopWidget().screenGeometry()
        self.resize(screen.width()/2,screen.height()/2)
        self.setWindowTitle('Chart')
        self.center()

    def center(self):
        screen=QtGui.QDesktopWidget().screenGeometry()
        size=self.geometry()
        self.move(screen.width()/2-size.width()/2,screen.height()/2-size.height()/2)

    def yRange(self,data):
        col=data.columns
        print(col)

    def defineRange(self):
        if self.xMove!=0:
            self.shownXray=self.xRay[-1-self.xMove-self.xCount:-self.xMove]
        else:
            self.shownXray=self.xRay[-1-self.xMove-self.xCount:]

        self.xList={}
        gap=self.areaWidth/len(list(self.shownXray))
        start=gap/2
        for i in self.shownXray:
            self.xList[i]=start
            start=start+gap


        self.shown=[]
        right=self.xRay[-1-self.xMove]
        left=self.xRay[-1-self.xMove-self.xCount]

        num=0
        self.Range=[]
        for n in self.data.copy():
            self.shown.append({})
            Max=[]
            Min=[]
            for type in n.keys():
                if type not in self.shown[num]:
                    self.shown[num][type]={}

                for name in n[type].keys():
                    self.shown[num][type][name]=[]
                    data=n[type][name][0]
                    show=data[data.time>=left]
                    show=show[show.time<=right]
                    xList=[]
                    for t in show.time:
                        xList.append(self.xList[t])
                    show.index=xList

                    self.shown[num][type][name].append(show)
                    self.shown[num][type][name].append(self.data[num][type][name][1])
                    if type=='candle':
                        Max.append(show['high'].max())
                        Min.append(show['low'].min())
                    elif type=='line':
                        Max.append(show['value'].max())
                        Min.append(show['value'].min())

            self.Range.append([max(Max),min(Min)])

            num=num+1


    def initCharts(self):
        chartsNum=len(self.shown)
        ch=self.areaHeight/(chartsNum+1)
        self.chartsGapLine=[2*ch]

        for i in range(1,chartsNum):
            self.chartsGapLine.append(ch+self.chartsGapLine[i-1])

        for n in self.shown:
            for Type in n.keys():
                if Type == 'candle':
                    for name in n[Type]:
                        data=n[Type][name]
                        candle=[]


    def paintEvent(self, event):
        self.areaHeight=self.height()-self.Xaxis
        self.areaWidth=self.width()-self.Yaxis

        self.xCount=int(self.Xalpha*self.areaWidth)

        qp=QtGui.QPainter()
        qp.begin(self)

        self.defineRange()
        self.initCharts()
        self.drawBackGround(event,qp)
        self.drawCharts(event,qp)

    def drawCharts(self,event,qp):

        for i in range(0,len(self.shown)):
            qp.save()

            qp.translate(0,self.chartsGapLine[i])
            qp.scale(1,-1)

            height=self.chartsGapLine[i]
            if i >0:
                height=height-self.chartsGapLine[i-1]

            self.drawCandle(event,qp,i,height)
            self.drawLines(event,qp,i,height)


            qp.scale(1,-1)
            self.drawLabel(event,qp)

            qp.restore()

    def drawLabel(self,event,qp):
        pass

    def drawCandle(self,event,qp,n,height):
        if 'candle' not in self.shown[n].keys():
            return

        for c in self.shown[n]['candle'].values():

            qp.setPen(c[1])
            modify=height/(self.Range[n][0]-self.Range[n][1])
            candle=c[0]
            w=self.areaWidth/len(self.xList)
            for i in candle.index:
                self.drawSingleCandle(qp,i,
                                      (candle.get_value(i,'open')-self.Range[n][1])*modify,
                                      (candle.get_value(i,'high')-self.Range[n][1])*modify,
                                      (candle.get_value(i,'low')-self.Range[n][1])*modify,
                                      (candle.get_value(i,'close')-self.Range[n][1])*modify,w,c[1])

    def drawSingleCandle(self,qp,x,open,high,low,close,width,color):

        rect=QtCore.QRectF(QtCore.QPointF(x-width/2.7,open),QtCore.QPointF(x+width/2.7,close))

        if open>close:
            qp.setBrush(QtGui.QColor(0,0,0))
        else:
            qp.setBrush(color)

        qp.drawLine(x,high,x,low)
        qp.drawRect(rect)



    def drawLines(self,event,qp,n,height):
        if 'line' not in self.shown[n].keys():
            return

        for l in self.shown[n]['line'].values():
            qp.setPen(l[1])
            modify=height/(self.Range[n][0]-self.Range[n][1])
            line=l[0]

            index=line.index
            prex=index[0]
            prey=(line.get_value(prex,'value')-self.Range[n][1])*modify
            for x in index[1:]:
                y=(line.get_value(x,'value')-self.Range[n][1])*modify
                qp.drawLine(prex,prey,x,y)
                prex=x
                prey=y


        pass

    def drawBackGround(self,event,qp):
        qp.setBrush(QtGui.QColor(0,0,0))
        qp.drawRect(0,0,self.width(),self.height())
        qp.setPen(QtGui.QColor(255,255,255))
        qp.drawLine(self.areaWidth,0,self.areaWidth,self.areaHeight)
        for l in self.chartsGapLine:
            qp.drawLine(0,l,self.width(),l)

    def importLine(self,name,df=None,time=None,line=None,n=0,color=None):
        if df is None:
            df=pandas.DataFrame({'time':time,'value':line})
        else:
            df.columns=['time','value']

        while len(self.data)<=n:
            self.data.append({})

        if 'line' not in self.data[n].keys():
            self.data[n]['line']={}

        if color is None:
            color=self.colors[0]
        elif isinstance(color,str):
            try:
                color=QtGui.QColor(color)
            except:
                color=self.colors[0]
        elif isinstance(color,int):
            try:
                color=self.colors[color]
            except:
                color=self.colors[0]

        def outXRay(x):
            return x not in self.xRay

        outxray=list(filter(outXRay,df.time.tolist()))
        if len(outxray)>0:
            self.xRay.extend(outxray)
            self.xRay.sort()

        self.data[n]['line'][name]=[df,color]

    def importCandle(self,name,df=None,time=None,open=None,high=None,low=None,close=None,n=0,color=None):
        if df is None:
            df=pandas.DataFrame({
                'time':time,'open':open,'high':high,'low':low,'close':close
            })
        else:
            df.columns=['time','open','high','low','close']

        while len(self.data)<=n:
            self.data.append({})

        if 'candle' not in self.data[n].keys():
            self.data[n]['candle']={}

        if color is None:
            color=self.colors[0]
        elif isinstance(color,str):
            try:
                color=QtGui.QColor(color)
            except:
                color=self.colors[0]
        elif isinstance(color,int):
            try:
                color=self.colors[color]
            except:
                color=self.colors[0]

        def outXRay(x):
            return x not in self.xRay

        outxray=list(filter(outXRay,df.time.tolist()))
        if len(outxray)>0:
            self.xRay.extend(outxray)
            self.xRay.sort()

        self.data[n]['candle'][name]=[df,color]



if  __name__ == '__main__':
    pass