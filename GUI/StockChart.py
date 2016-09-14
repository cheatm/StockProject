from PyQt4 import QtCore,QtGui
import pandas,sys,time

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

    yLabel=[]

    def __init__(self,parent=None,Xaxis=15,Yaxis=80):
        QtGui.QWidget.__init__(self,parent)

        self.initWidget()

        self.Xaxis=Xaxis
        self.Yaxis=Yaxis
        self.highEdge=0
        self.lowEdge=0
        self.leftEdge=0
        self.rightEdge=0
        self.areaHeight=self.height()-self.Xaxis-self.highEdge-self.lowEdge
        self.areaWidth=self.width()-self.Yaxis-self.leftEdge-self.rightEdge

        self.xCount=int(self.Xalpha*self.areaWidth)


        self.command={
            QtCore.Qt.Key_Down:self.down,
            QtCore.Qt.Key_Up:self.up,
            QtCore.Qt.Key_Left:self.left,
            QtCore.Qt.Key_Right:self.right
            }

    def mousePressEvent(self, event):
        self.setMouseTracking(self.hasMouseTracking()==False )
        self.posx=event.x()
        self.posy=event.y()
        self.locate=self.locateX(event.x())
        print(self.locate)
        self.update()

    def mouseMoveEvent(self,event):
        self.posx=event.x()
        self.posy=event.y()
        self.locate=self.locateX(event.x())
        print(self.locate)
        self.update()


    def keyPressEvent(self, event):

        if event.key() in self.command.keys():

            self.command[event.key()]()

    def wheelEvent(self, event):

        if event.delta()>0:
            self.up()
        else:
            self.down()

    def left(self):
        if self.xMove+self.xCount<len(self.xRay):
            self.xMove=self.xMove+1
            self.repaint()

    def right(self):
        if self.xMove-1>=0:
            self.xMove=self.xMove-1
            self.repaint()

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
                        xList.append(self.leftEdge+self.xList[t])
                    show.index=xList

                    self.shown[num][type][name].append(show)
                    self.shown[num][type][name].append(self.data[num][type][name][1])
                    if type=='candle':
                        Max.append(show['high'].max()*1.03)
                        Min.append(show['low'].min()*0.97)
                    elif type=='line':
                        Max.append(show['value'].max()*1.03)
                        Min.append(show['value'].min()*0.97)
                    elif type=='hist':
                        h=abs(show['value'].max())
                        l=abs(show['value'].min())
                        Max.append(max(h,l)*1.03)
                        Min.append(-max(h,l)*1.03)


            self.Range.append([max(Max),min(Min)])

            num=num+1

    def initCharts(self):
        chartsNum=len(self.shown)
        ch=self.areaHeight/(chartsNum+1)
        self.chartsGapLine=[2*ch+self.highEdge]

        for i in range(1,chartsNum):
            self.chartsGapLine.append(ch+self.chartsGapLine[i-1])

    def paintEvent(self, event):
        self.areaHeight=self.height()-self.Xaxis-self.highEdge-self.lowEdge
        self.areaWidth=self.width()-self.Yaxis-self.leftEdge-self.rightEdge
        print()
        self.xCount=int(self.Xalpha*self.areaWidth)
        if self.xCount>len(self.xRay)-1:
            self.xCount=len(self.xRay)-1

        qp=QtGui.QPainter()
        qp.begin(self)

        self.defineRange()
        self.initCharts()
        self.drawBackGround(event,qp)
        self.drawCharts(event,qp)

    def drawCrossLine(self,event,qp):
        if self.hasMouseTracking():

            qp.setPen(QtGui.QColor(255,255,255))

            qp.drawLine(QtCore.QPoint(self.posx,0),QtCore.QPoint(self.posx,self.areaHeight))
            qp.drawLine(QtCore.QPoint(0,self.posy),QtCore.QPoint(self.areaWidth,self.posy))



    def drawCharts(self,event,qp):

        for i in range(0,len(self.shown)):
            qp.save()

            qp.translate(0,self.chartsGapLine[i])
            qp.scale(1,-1)

            height=self.chartsGapLine[i]
            if i >0:
                height=height-self.chartsGapLine[i-1]
            modify=height/(self.Range[i][0]-self.Range[i][1])
            self.drawHist(event,qp,i,modify,height)
            self.drawCandle(event,qp,i,modify)
            self.drawLines(event,qp,i,modify)

            qp.scale(1,-1)

            self.drawYLabel(event,qp,i,modify,self.yLabel[i])
            self.drawShortName(event,qp,i,height)

            qp.restore()
        self.drawXLabel(event,qp,self.Xaxis*0.8)
        self.drawCrossLine(event,qp)

    def locateX(self,X):
        Min=X
        value=X
        for i in self.xList.values():
            if abs(X-i)<Min:
                Min=abs(X-i)
                value=i
        return value



    def drawShortName(self,event,qp,n,height,size=10):
        qp.translate(0,-height)
        qp.setFont(QtGui.QFont('ShortName',size))
        pos=QtCore.QPointF(2,2+size)

        for tp in sorted(self.shown[n].keys()):
            t=self.shown[n][tp]
            for name in t.keys():
                c=t[name]
                qp.setPen(c[1])
                qp.setBrush(c[1])
                col=c[0].columns.tolist()
                col.pop(0)

                pandas.DataFrame()
                x=c[0].index[-1]
                out=name

                if self.hasMouseTracking():
                    x=self.locate

                try:
                    if len(col)==1:
                        out="%s:%s" % (out,c[0].get_value(x,col[0]))
                    else:
                        for s in col:
                            out="%s %s:%s" % (out,s,c[0].get_value(x,s))
                except :
                    if len(col)==1:
                        out="%s:%s" % (out,c[0].get_value(c[0].index[-1],col[0]))
                    else:
                        for s in col:
                            out="%s %s:%s" % (out,s,c[0].get_value(c[0].index[-1],s))

                qp.drawText(pos,out)

                if tp=='candle':
                    pos.setY(pos.y()+2+size)
                else:
                    pos.setX(pos.x()+2+len(out)*size/1.3)

    def drawYLabel(self,event,qp,i,modify,args,size=10):
        qp.setPen(QtGui.QColor(255,255,255))
        qp.setFont(QtGui.QFont('Ylabel',size))
        for a in args:
            y=-(a-self.Range[i][1])*modify
            qp.drawLine(QtCore.QPointF( self.areaWidth+self.leftEdge,y),
                        QtCore.QPointF(self.areaWidth+self.leftEdge+5,y))
            qp.drawText(QtCore.QPointF(self.areaWidth+self.leftEdge+5,y+size/2),str(a))

    def drawXLabel(self,event,qp,size):
        qp.save()
        qp.translate(0,self.areaHeight+self.highEdge)
        qp.setPen(QtGui.QColor(255,255,255))

        qp.setFont(QtGui.QFont('Xlabel',size))
        l=len(self.xList)

        last=0
        for t in sorted(self.xList.keys()):
            text=time.strftime('%Y/%m/%d',time.gmtime(t))
            x=self.xList[t]
            if x>last:
                qp.drawLine(x,0,x,-2)
                qp.drawText(x,2+size,text)
                last=x+len(text)*size
        qp.restore()

    def drawHist(self,event,qp,n,modify,height):
        if 'hist' not in self.shown[n].keys():
            return
        qp.translate(0,height/2)

        for c in self.shown[n]['hist'].values():
            qp.setPen(c[1])
            qp.setBrush(c[1])
            hist=c[0]
            w=self.areaWidth/len(self.xList)
            for i in hist.index:
                y=(hist.get_value(i,'value')*modify)

                qp.drawRect(QtCore.QRectF(QtCore.QPointF(i-w/2.7,0),QtCore.QPointF(i+w/2.7,y)))

        qp.translate(0,-height/2)

    def drawCandle(self,event,qp,n,modify):
        if 'candle' not in self.shown[n].keys():
            return

        for c in self.shown[n]['candle'].values():

            qp.setPen(c[1])

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

    def drawLines(self,event,qp,n,modify):
        if 'line' not in self.shown[n].keys():
            return

        for l in self.shown[n]['line'].values():
            qp.setPen(l[1])

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
        qp.drawLine(self.leftEdge+self.areaWidth,self.highEdge,self.leftEdge+self.areaWidth,self.highEdge+self.areaHeight)
        qp.drawLine(self.leftEdge,self.highEdge,self.leftEdge,self.highEdge+self.areaHeight)
        for l in self.chartsGapLine:
            qp.drawLine(self.leftEdge,l,self.width()-self.rightEdge,l)

    def importHist(self,name,df=None,time=None,hist=None,n=0,color=None,label=None):
        if df is None:
            df=pandas.DataFrame({'time':time,'value':hist})
        else:
            df.columns=['time','value']

        while len(self.data)<=n:
            self.data.append({})
            self.yLabel.append([])

        if 'hist' not in self.data[n].keys():
            self.data[n]['hist']={}

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
        elif isinstance(color,list):
            color=QtGui.QColor(*color[0:3])

        def outXRay(x):
            return x not in self.xRay

        outxray=list(filter(outXRay,df.time.tolist()))
        if len(outxray)>0:
            self.xRay.extend(outxray)
            self.xRay.sort()

        self.data[n]['hist'][name]=[df,color]
        if label is not None:
            self.yLabel[n].extend(label)

    def importLine(self,name,df=None,time=None,line=None,n=0,color=None,label=None):
        if df is None:
            df=pandas.DataFrame({'time':time,'value':line})
        else:
            df.columns=['time','value']

        while len(self.data)<=n:
            self.data.append({})
            self.yLabel.append([])

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
        elif isinstance(color,list):
            color=QtGui.QColor(*color[0:3])

        def outXRay(x):
            return x not in self.xRay

        outxray=list(filter(outXRay,df.time.tolist()))
        if len(outxray)>0:
            self.xRay.extend(outxray)
            self.xRay.sort()

        self.data[n]['line'][name]=[df,color]
        if label is not None:
            self.yLabel[n].extend(label)

    def importCandle(self,name,df=None,time=None,open=None,high=None,low=None,close=None,n=0,color=None,label=None):
        if df is None:
            df=pandas.DataFrame({
                'time':time,'open':open,'high':high,'low':low,'close':close
            })
        else:
            df.columns=['time','open','high','low','close']

        while len(self.data)<=n:
            self.data.append({})
            self.yLabel.append([])

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
        elif isinstance(color,list):
            color=QtGui.QColor(*color[0:3])

        def outXRay(x):
            return x not in self.xRay

        outxray=list(filter(outXRay,df.time.tolist()))
        if len(outxray)>0:
            self.xRay.extend(outxray)
            self.xRay.sort()

        self.data[n]['candle'][name]=[df,color]
        if label is not None:
            self.yLabel[n].extend(label)



if  __name__ == '__main__':
    pass