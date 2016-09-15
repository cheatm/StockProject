__author__ = 'CaiMeng'

import sys,pandas,time
import EconomicData
from PyQt4 import QtGui,QtCore
import HKStock,indicator

class StockChart(QtGui.QMainWindow):

    xRay=[]

    YR={}

    # numbers to adjust Y axis of each graph
    ymodify={}

    # data to be shown in the graph
    ShownGraph=[]
    ShownGraphDict={}

    GHights=[]

    # all data to be drawn
    Graph=[]

    alphaX=0.2

    # points data to be shown in the graph
    Points={}

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

    # color for each line or candle or ....
    chartColor={}

    # xAxis to show date
    xAxis=[]

    # yAxis to show value
    yAxis=[]

    # size of xAxis and yAxis
    xSize=20
    ySize=50

    # supportLines
    extraLines=[]

    # extra y label to draw
    yLabel={}

    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)

        self.xCounts=(int)(self.width()*self.alphaX)
        self.xMove=0

        self.command={
            QtCore.Qt.Key_Down:self.down,
            QtCore.Qt.Key_Up:self.up,
            QtCore.Qt.Key_Left:self.left,
            QtCore.Qt.Key_Right:self.right
            }

        self.BGcolor= QtGui.QColor(0,0,0)
        self.initWidget()
        # self.setToolTip('widget')
        # self.initBottoms()

    def importHistogram(self,name=None,hist=None,figure=0,color=None):
        while len(self.Graph)<=figure:
            self.Graph.append({'Hist':{}})
            self.ShownGraph.append({'Hist':{}})

        if name is None:
            name='Hist%s' % len(self.Graph[figure]['Hist'])

        if color is not None:
            if type(color)==type([]):
                self.chartColor[name]=QtGui.QColor(color[0],color[1],color[2])
            elif type(color)==type(''):
                self.chartColor[name]=QtGui.QColor(color)
            else:
                self.chartColor[name]=self.colors[len(self.Graph[figure]['Hist'])]
        else:
            self.chartColor[name]=self.colors[len(self.Graph[figure]['Hist'])]

        if 'Hist' not in  self.Graph[figure].keys():
            self.Graph[figure]['Hist']={}

        self.Graph[figure]['Hist'][name]=hist

        def outXRay(x):
            return x not in self.xRay

        outxray=list(filter(outXRay,hist[0]))
        if len(outxray)>0:
            self.xRay.extend(outxray)
            self.xRay.sort()
        pass

    def importLine(self,name=None,line=None,figure=0,color=None,**args):

        while len(self.Graph)<=figure:
            self.Graph.append({'line':{}})
            self.ShownGraph.append({'line':{}})


        if name is None:
            name='Line%s' % len(self.Graph[figure]['line'])

        if color is not None:
            if type(color)==type([]):
                self.chartColor[name]=QtGui.QColor(color[0],color[1],color[2])
            elif type(color)==type(''):
                self.chartColor[name]=QtGui.QColor(color)
            else:
                self.chartColor[name]=self.colors[len(self.Graph[figure]['line'])]
        else:
            self.chartColor[name]=self.colors[len(self.Graph[figure]['line'])]

        if 'line' not in self.Graph[figure].keys():
            self.Graph[figure]['line']={}

        self.Graph[figure]['line'][name]=line

        def outXRay(x):
            return x not in self.xRay

        outxray=list(filter(outXRay,line[0]))
        if len(outxray)>0:
            self.xRay.extend(outxray)
            self.xRay.sort()


    def importCandle(self,name=None,candle=None,figure=0,color=None):
        while len(self.Graph)<=figure:
            self.Graph.append({'candle':{}})
            self.ShownGraph.append({'candle':{}})


        if name is None:
            name='Candle%s' % len(self.Graph[figure]['candle'])

        if color is not None:

            if type(color)==type([]):
                self.chartColor[name]=QtGui.QColor(color[0],color[1],color[2])
            elif type(color)==type(''):
                self.chartColor[name]=QtGui.QColor(color)
            else:
                self.chartColor[name]=self.colors[len(self.Graph[figure]['candle'])]
        else:
            self.chartColor[name]=self.colors[len(self.Graph[figure]['candle'])]

        if 'candle' not in self.Graph[figure].keys():
            self.Graph[figure]['candle']={}

        self.Graph[figure]['candle'][name]=candle

        def outXRay(x):
            return x not in self.xRay

        outxray=list(filter(outXRay,candle[0]))
        if len(outxray)>0:
            self.xRay.extend(outxray)
            self.xRay.sort()

    def left(self):
        if self.xMove+self.xCounts<len(self.xRay):
            self.xMove=self.xMove+1
            self.repaint()



    def right(self):
        if self.xMove-1>=0:
            self.xMove=self.xMove-1
            self.repaint()



    def down(self):
        self.alphaX*=0.8
        self.repaint()


    def up(self):
        self.alphaX/=0.8
        self.repaint()


    def initWidget(self):

        screen=QtGui.QDesktopWidget().screenGeometry()
        self.resize(screen.width()/2,screen.height()/2)
        self.setWindowTitle('Icon')
        self.center()


    def initBottoms(self):
        quit=QtGui.QPushButton('Close',self)
        quit.setGeometry(10,10,60,35)
        self.connect(quit,QtCore.SIGNAL('clicked()'),self.output )

    def paintEvent(self, event):

        # Chart area size
        self.areaHeight=self.height()-self.xSize
        self.areaWidth=self.width()-self.ySize

        self.GHights=[2/(1+len(self.Graph))*self.areaHeight]
        for a in range(1,len(self.Graph)):
            self.GHights.append(1/(1+len(self.Graph))*self.areaHeight)

        self.xCounts=(int)(self.width()*self.alphaX)

        self.defineRange()

        qp=QtGui.QPainter()
        qp.begin(self)
        qp.save()

        for f in range(0,len(self.Graph)):

            self.drawGraph(event,qp,f,height=self.GHights[f])

        self.drawXaxis(event,qp)

        qp.restore()
        self.drawCrossLine(event,qp)

        qp.end()

    def drawCrossLine(self,event,qp):
        if self.hasMouseTracking():

            textSize=self.xSize*3/5
            qp.setPen(QtGui.QColor(255,255,255))
            qp.setFont(QtGui.QFont('fontCross',textSize))

            qp.drawLine(QtCore.QPoint(self.posx,0),QtCore.QPoint(self.posx,self.areaHeight))
            qp.drawLine(QtCore.QPoint(0,self.posy),QtCore.QPoint(self.areaWidth,self.posy))

            date=self.toStrDate(self.crossLineX)
            qp.drawText(self.posx+2,self.areaHeight-2,date)


    def getCrossLineXValue(self):
        gap=self.areaWidth/len(self.shownX)/2
        for t in self.shownX.keys():
            if abs(self.posx-self.shownX[t])<=gap:
                date=self.toStrDate(t)
                return(t)


    def drawGraph(self,event,qp,num,height):

        qp.restore()
        qp.save()

        startY=0
        for n in range(0,num):
            startY=startY+self.GHights[n]
        self.drawBackGround(event,qp,QtCore.QRect(0,startY,self.width(),height),color=self.BGcolor)


        if self.hasMouseTracking():
            self.drawLabel(event,qp,num,y=startY,x=self.crossLineX)
        else:
            self.drawLabel(event,qp,num,y=startY)


        qp.setPen(QtGui.QColor(255,255,255))
        qp.drawLine(QtCore.QPoint(0,startY),QtCore.QPoint(self.width(),startY))
        qp.drawLine(QtCore.QPoint(self.areaWidth,startY),QtCore.QPoint(self.areaWidth,startY+self.GHights[num]))

        def func(dic):
            l=0
            if type(dic)==type({}):
                for d in dic.values():
                    l=l+func(d)
            elif type(dic)==type([]):
                return len(dic)
            return (l)

        qp.scale(1,-1)
        qp.translate(0,-startY-height)

        if func(self.ShownGraph[num])>=2:

            YR=self.Yrange(num)

            self.YR[num]=YR

            self.ymodify[num]=(YR[0]-YR[1])/height

            # draw charts
            self.drawHist(event,qp,num,height=height/2)
            self.drawLines(event,qp,num)
            self.drawCandles(event,qp,num)

        qp.scale(1,-1)

        self.drawYaxis(event,qp,num,height=height)

    def drawXaxis(self,event,qp):
        self.drawBackGround(event,qp,QtCore.QRect(0,0,self.width(),self.xSize))
        qp.setPen(QtGui.QColor(255,255,255))

        # draw X line
        qp.drawLine(0,0,self.width(),0)

        textSize=self.xSize*3/5
        font=QtGui.QFont('xAxis',textSize)
        qp.setFont(font)

        last=0
        for xa in sorted(self.shownX.keys()):

            x=self.shownX[xa]

            date=self.toStrDate(xa)

            if x > last :
                qp.drawLine(x,0,x,-4)
                qp.drawText(x,textSize*4/3,date)
                last = x+len(date)*(textSize)
        pass

    def toStrDate(self,seconds):
        date=time.localtime(seconds)
        return (time.strftime('%Y/%m/%d %H:%M',date))

    yLnumber={}

    def setYlabel(self,value=None,count=None,figure=0,):
        if value is not None:
            if figure not in self.yLabel.keys():
                self.yLabel[figure]=[value]
            else:
                self.yLabel[figure].append(value)

        if count is not None:
            if figure not in self.yLnumber.keys():
                self.yLnumber[figure]=count
            else:
                self.yLnumber[figure]=count

    def drawYaxis(self,event,qp,num=0,lines=2,height=0):
        R=self.YR[num][0]-self.YR[num][1]

        textSize=self.xSize*3/5
        font=QtGui.QFont('yAxis',textSize)
        qp.setFont(font)
        qp.setPen(QtGui.QColor(255,255,255))

        if num in self.yLabel.keys():
            for value in self.yLabel[num]:
                y=-(value-self.YR[num][1])/self.ymodify[num]
                if 0<-y and -y<height:

                    qp.drawLine(self.areaWidth,y,self.areaWidth-4,y)
                    qp.drawText(self.areaWidth+1,y+textSize/2,' %s' % value)
                pass
        else:
            if num not in self.yLnumber.keys():
                self.yLnumber[num]=2
            gap=R/(self.yLnumber[num]+1)
            for i in range(0,self.yLnumber[num]):
                value=self.YR[num][1]+(i+1)*gap
                y=-(value-self.YR[num][1])/self.ymodify[num]
                qp.drawLine(self.areaWidth,y,self.areaWidth-4,y)
                qp.drawText(self.areaWidth+1,y+textSize/2,' %s' % value)
                pass

        pass

    def importExtraLine(self,point1,point2,num=0):
        while len(self.extraLines)<=num:
            self.extraLines.append([])
        self.extraLines[num].append([point1,point2])

        pass

    def drawExtraLine(self,event,qp,num):

        pass

    def drawLabel(self,event,qp,num=0,size=10,y=0,x=None):
        c=2
        font=QtGui.QFont('label',size)
        font.setWeight(63)

        def findIndex(lis,value):
            if value is not None:
                # if value in lis:
                #     return (lis.index(value))
                out=abs(lis[-1]-value)
                pos=0
                for i in reversed(lis):

                    diff=abs(i-value)
                    if diff>out:
                        return pos
                    out=diff
                    pos=pos-1

            return (-1)

        if x is not None:
            for ct in self.ShownGraph[num].values():
                for name in ct.keys():
                    qp.setPen(self.chartColor[name])
                    qp.setFont(font)

                    label="%s:" % name

                    for v in ct[name][1:]:
                        label=label+str(v[ findIndex(ct[name][0],x) ])+" "

                    qp.drawText(c,y+size+2,label)
                    c=c+size*len(label)*4/5
        else:
            for ct in self.Graph[num].values():
                for name in ct.keys():
                    qp.setPen(self.chartColor[name])
                    qp.setFont(font)

                    label="%s:" % name

                    for v in ct[name][1:]:
                        label=label+str(v[ -1 ])+" "

                    qp.drawText(c,y+size+2,label)
                    c=c+size*len(label)*4/5

    def Yrange(self,num):
        maxY=[]
        minY=[]

        g=self.ShownGraph[num]
        for type in g.keys():

            if type=='line':
                for name in g[type].keys():
                    if len(g[type][name])>=2:
                        maxY.append(max( g[type][name][1]))
                        minY.append(min( g[type][name][1]))
            if type=='candle':

                for name in g[type].keys():
                    if len(g[type][name])>=2:
                        maxY.append(max( g[type][name][2]))
                        minY.append(min( g[type][name][3]))

            if type=='Hist':
                for name in g[type].keys():
                    if len(g[type][name])>=2:
                        maxY.append(max( g[type][name][1]))
                        minY.append(min( g[type][name][1]))
                Max=max(maxY)
                Min=min(minY)
                if abs(Max)>=abs(Min):
                    return [abs(Max),-abs(Max)]
                else:
                    return [abs(Min),-abs(Min)]


        if len(maxY) and len(minY):
            return [max(maxY),min(minY)]
        else :
            return [1,0]


    def defineRange(self):
        if self.xCounts+self.xMove>len(self.xRay):
            self.xCounts=len(self.xRay)-self.xMove
        leftX=self.xRay[-self.xCounts-self.xMove]
        rightX=self.xRay[-1-self.xMove]
        self.XR=[rightX,leftX]
        self.xmodify=(rightX-leftX)/self.areaWidth

        shownXray=[]
        if self.xMove==0:
            shownXray=self.xRay[-self.xCounts-self.xMove:]
        else :
            shownXray=self.xRay[-self.xCounts-self.xMove:-self.xMove]
        self.shownX={0:0}
        for x in range(0,len(shownXray)):
            self.shownX[shownXray[x]]=(x+0.5)*self.areaWidth/len(shownXray)

            pass


        # former=0
        # for k in sorted(self.shownX.keys()):
        #
        #
        #     print('%s:%s' % (k,self.shownX[k]-former))
        #     former=self.shownX[k]
        #
        # print(len(self.shownX))

        def xRange(List,mi,ma):
            Mi=None
            Ma=None
            for a in range(0,len(List)):
                if Mi is None:
                    if List[a]>=mi:
                        Mi=a
                        break
            for a in reversed(range(0,len(List))):
                if Ma is None:
                    if List[a]<=ma:
                        Ma=a
                        break
            return([Mi,Ma])

        gn=0

        for g in self.Graph:
            for l in g.keys():
                self.ShownGraph[gn][l]={}
                for name in g[l].keys():
                    xrange=xRange(g[l][name][0],leftX,rightX)

                    self.ShownGraph[gn][l][name]=[]

                    for data in g[l][name]:
                        if None not in xrange:

                            self.ShownGraph[gn][l][name].append(data[xrange[0]:xrange[1]])

            gn=gn+1

    def wheelEvent(self, event):

        if event.delta()>0:
            self.up()
        else:
            self.down()

    def mousePressEvent(self, event):
        self.setMouseTracking(self.hasMouseTracking()==False )
        self.posx=event.x()
        self.posy=event.y()
        self.crossLineX=self.getCrossLineXValue()
        self.update()


    posx=0
    posy=0

    def mouseMoveEvent(self, event):
        self.posx=event.x()
        self.posy=event.y()
        self.crossLineX=self.getCrossLineXValue()
        self.update()

    def keyPressEvent(self, event):

        if event.key() in self.command.keys():

            self.command[event.key()]()


    def drawCandles(self,event,qp,num=0):

        if 'candle' not in self.ShownGraph[num].keys():
            return (None)

        candle=self.ShownGraph[num]['candle']

        for k in candle.keys():
            v=candle[k]

            candlewidth=self.areaWidth/len(self.shownX)*0.8
            qp.setPen(self.chartColor[k])

            for i in range(0,len(v[0])):
                x=self.shownX[v[0][i]]

                single=[x]
                for s in range(1,5):
                    single.append((v[s][i]-self.YR[num][1])/self.ymodify[num])

                self.drawSingleCandle(event,qp,single,candlewidth,self.chartColor[k])


    def drawSingleCandle(self,event,qp,candle,width,color):

        if candle[1]<candle[4]:
            qp.setBrush(self.BGcolor)
            qp.drawLine(QtCore.QPointF(candle[0],candle[3]),QtCore.QPointF(candle[0],candle[1]))
            qp.drawLine(QtCore.QPointF(candle[0],candle[2]),QtCore.QPointF(candle[0],candle[4]))

        else:
            qp.setBrush(color)
            qp.drawLine(QtCore.QPointF(candle[0],candle[2]),QtCore.QPointF(candle[0],candle[3]))

        rect=QtCore.QRectF(QtCore.QPointF(candle[0]-width/2,candle[1]),QtCore.QPointF(candle[0]+width/2,candle[4]))

        qp.drawRect(rect)

        pass

    def drawLines(self,event,qp,num=0):

        if 'line' not in self.ShownGraph[num].keys():
            return (None)

        Line=self.ShownGraph[num]['line']

        c=0

        # k: name of each Line
        for k in Line.keys():

            v=Line[k]
            if len(v)==0:
                continue

            points=[]

            x,y=0,0

            self.Points[k]={'x':[],'y':[]}

            for i in range(0,len(v[0])):
                x=self.shownX[v[0][i]]
                y=(v[1][i]-self.YR[num][1])/self.ymodify[num]

                points.append(QtCore.QPointF(x,y))
                self.Points[k]['x'].append(x)
                self.Points[k]['y'].append(y)

            qp.setPen(self.chartColor[k])
            for p in range(1,len(points)):
                qp.drawLine(points[p-1],points[p])

    def drawHist(self,event,qp,num=0,height=0):

        if 'Hist' not in self.ShownGraph[num].keys():
            return (None)
        hist=self.ShownGraph[num]['Hist']



        for k in hist.keys():
            v=hist[k]
            qp.setPen(self.chartColor[k])
            qp.setBrush(self.chartColor[k])

            width=self.areaWidth/len(v[0])*0.5

            for i in range(0,len(v[0])):
                x=self.shownX[v[0][i]]
                y=(v[1][i])/self.ymodify[num]+height



                if width>=1:
                    qp.drawRect(QtCore.QRectF(QtCore.QPointF(x-width/2,y),QtCore.QPointF(x+width/2,height)))
                else :
                    qp.drawLine(QtCore.QPointF(x,y),QtCore.QPointF(x,height))


    def drawSquare(self,event,qp):
        color=QtGui.QColor(255,255,255)
        qp.setBrush(color)
        qp.drawRect(20,20,10,30)

    def drawBackGround(self,event,qp,rect,color=QtGui.QColor(0,0,0)):

        qp.setPen(color)
        qp.setBrush(color)
        qp.drawRect(rect)

    def center(self):
        screen=QtGui.QDesktopWidget().screenGeometry()
        size=self.geometry()
        self.move(screen.width()/2-size.width()/2,screen.height()/2-size.height()/2)

    def output(self):
        print('out')

class RRG_M(QtGui.QMainWindow):
    from math import cos,sin,tan,atan2

    highedge=0
    lowedge=0
    leftedge=0
    rightedge=0

    period=10

    data={}

    colors=[

        QtGui.QColor('cyan'),
        QtGui.QColor('green'),
        QtGui.QColor('blue'),
        QtGui.QColor('gray'),
        QtGui.QColor('red'),
        QtGui.QColor('magenta'),
        QtGui.QColor('white'),
        QtGui.QColor('yellow')
    ]

    graphColor={}

    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.initWidget()

    def initWidget(self):

        screen=QtGui.QDesktopWidget().screenGeometry()
        self.resize(screen.width()/2,screen.height()/2)
        self.setWindowTitle('RRG_M')
        self.center()

    def center(self):
        '''
        move to center of the monitor
        :return:
        '''
        screen=QtGui.QDesktopWidget().screenGeometry()
        size=self.geometry()
        self.move(screen.width()/2-size.width()/2,screen.height()/2-size.height()/2)

    def importData(self,name,time=None,x=None,y=None,DF=None,color=None):
        '''

        :param name:
        :param time: list of time
        :param x: list of numbers on x axis
        :param y: list of numbers on y axis
        :param DF:
            DataFrame() with 3 columns and it will be transform to ['time','x','y']
            sample:
                          time    RS_Ratio   momentum5
                5   1471190400  100.184223  101.723444
                6   1471276800  100.421118  101.633165
                7   1471363200  100.868189  102.140967
                8   1471449600  100.920851  102.770772
                9   1471536000  100.341464  101.229403

        :param color:
        :return:
        '''
        if DF is None:
            if len(time)!=x or len(time)!=y:
                print('length not equal')
                return 0

            if self.period>len(time):
                self.period=len(time)

            self.data[name]=pandas.DataFrame({'time':time,'x':x,'y':y})
        else:
            if self.period>len(DF.index):
                self.period=len(DF.index)

            DF.columns=['time','x','y']
            self.data[name]=DF

        if color is None:
            l=len(self.graphColor)
            self.graphColor[name]=self.colors[l]

    def importPrice(self,name,time,price,short=60,long=130,color=None):
        '''
        import price data and transform to momentum which should be saved in self.data
        :param name:
        :param time: list,series
        :param price: list,series
        :param short: shortPeriod
        :param long: longPeriod
        :return:
        '''
        if len(time) != len(price):
            print('length not equal')
            return 0

        shortmom=indicator.momentum(time,price,short)
        longmom=indicator.momentum(time,price,long)
        shortmom.columns=['time','x']
        longmom.columns=['time','y']

        self.data[name]=shortmom.merge(longmom,how='inner',on='time')

        if color is None:
            l=len(self.graphColor)
            self.graphColor[name]=self.colors[l]

        print(self.graphColor)



    def ArrangeData(self):
        '''
        create self.Graph which contains the data that should be shown on the monitor
        :return:
        '''

        self.Graph={}

        for k in self.data.keys():
            data=self.data[k]
            start=data.index.tolist()[-self.period]

            self.Graph[k]=data[data.index>=start]

        Max=[]
        Min=[]
        for v in self.Graph.values():

            for c in ['x','y']:
                Max.append(max(v[c].tolist()))
                Min.append(min(v[c].tolist()))

        MaxValue=max(Max)-100
        MinValue=min(Min)-100

        edge=max([abs(MaxValue),abs(MinValue)])*1.1

        halfY=(self.height()-self.highedge-self.lowedge)/2
        halfX=(self.width()-self.leftedge-self.rightedge)/2

        for v in self.Graph.keys():
            graph=self.Graph[v]
            points=[]
            for i in graph.index:

                x=(graph.get_value(i,'x')-100)/edge*halfX
                y=(graph.get_value(i,'y')-100)/edge*halfY

                points.append(QtCore.QPointF(x,y))


            self.Graph[v].insert(3,'QPoint',points)


        rect=QtCore.QRectF(QtCore.QPointF(halfX,halfY),
                           QtCore.QPointF(-halfX,-halfY))

        cdepth=100
        calpha=35
        self.BackGround={
            'back':rect,
            'x':QtCore.QLineF(-halfX,0,halfX,0),
            'y':QtCore.QLineF(0,-halfY,0,halfY),
            'leftup':[QtCore.QRectF(QtCore.QPointF(-halfX,halfY),QtCore.QPointF(0,0)),QtGui.QColor(0,cdepth,cdepth,calpha)],
            'rightup':[QtCore.QRectF(QtCore.QPointF(halfX,halfY),QtCore.QPointF(0,0)),QtGui.QColor(cdepth,0,cdepth,calpha)],
            'leftdown':[QtCore.QRectF(QtCore.QPointF(-halfX,-halfY),QtCore.QPointF(0,0)),QtGui.QColor(cdepth,cdepth,0,calpha)],
            'rightdown':[QtCore.QRectF(QtCore.QPointF(halfX,-halfY),QtCore.QPointF(0,0)),QtGui.QColor(cdepth,cdepth,cdepth,calpha)]

        }

    def paintEvent(self,event):
        self.ArrangeData()

        qp=QtGui.QPainter()
        qp.begin(self)

        qp.translate(self.width()/2,self.height()/2)
        qp.scale(1,-1)
        self.drawBackGround(event,qp,self.BackGround)

        size=10
        c=0
        for k in self.Graph.keys():

            name="%s:%s,%s" % (k,
                               int(self.Graph[k]['x'].tolist()[-1]*100)/100,
                               int(self.Graph[k]['y'].tolist()[-1]*100)/100)
            self.drawLines(event,qp,name,self.Graph[k]['QPoint'],self.graphColor[k])
            labelPoint=QtCore.QPointF(-self.width()/2+self.leftedge,self.height()/2-self.highedge-c*size)
            self.drawLabel(event,qp,name,labelPoint,size=size)
            c=c+1.1

    def drawLines(self,event,qp,name,points,color):
        qp.setPen(color)
        qp.setBrush(color)

        index=points.index.tolist()

        for i in index[:-1]:
            qp.drawLine(points[i],points[i+1])

            qp.drawEllipse(points[i],2,2)

        self.drawArrow(event,qp,points[index[-2]],points[index[-1]])

    def drawLabel(self,event,qp,name,point,size=10):
        font=QtGui.QFont('label',size)
        qp.setFont(font)

        actual=QtCore.QPointF(point.x()+10,-point.y()+10)
        qp.scale(1,-1)
        qp.drawText(actual,name)
        qp.scale(1,-1)

    def drawArrow(self,event,qp,last,end):
        print(last,end)
        length=8
        degrees=0.4
        angle=self.atan2(end.y()-last.y(),end.x()-last.x())+3.1415926
        x1=end.x()+length*self.cos(angle-degrees)
        y1=end.y()+length*self.sin(angle-degrees)
        x2=end.x()+length*self.cos(angle+degrees)
        y2=end.y()+length*self.sin(angle+degrees)

        path=QtGui.QPainterPath()
        path.moveTo(end)
        path.lineTo(QtCore.QPointF(x1,y1))
        path.lineTo(QtCore.QPointF(x2,y2))
        path.lineTo(end)

        qp.drawPath(path)

    def drawBackGround(self,event,qp,backGround,backcolor=QtGui.QColor(0,0,0),linecolor=QtGui.QColor(255,255,255)):

        qp.setPen(backcolor)
        qp.setBrush(backcolor)
        qp.drawRect(backGround['back'])
        qp.setPen(linecolor)
        qp.drawLine(backGround['x'])
        qp.drawLine(backGround['y'])
        for i in ['leftup','leftdown','rightup','rightdown']:
            qp.setBrush(backGround[i][1])
            qp.drawRect(backGround[i][0])

def printData():
    print(EconomicData.getYahooData())

def showChart():
    app=QtGui.QApplication(sys.argv)
    window=StockChart()

    HSI=pandas.read_excel('%s.xlsx' % HKStock.HKindex[0])
    date=[]
    for d in HSI.tradeDate:
        date.append(time.mktime(time.strptime(d,'%Y-%m-%d')))
    
    window.importCandle(name=HKStock.HKindex[0],candle=[
        date,HSI.openIndex.tolist(),HSI.highestIndex.tolist(),HSI.lowestIndex.tolist(),HSI.closeIndex.tolist()
    ])

    for i in range(0,6):


        data=pandas.read_excel('%s.xlsx' % HKStock.HKindex[i])
        ind=indicator.MOMENTUM(data,60,'closeIndex')

        date=[]
        for d in data.tradeDate:
            date.append(time.mktime(time.strptime(d,'%Y-%m-%d')))

        window.importLine(name=HKStock.HKindex[i],line=[ind.time.tolist(),ind.MOMENTUM.tolist()],figure=1)
    window.show()
    sys.exit(app.exec_())



def showMainWindow():
    print('start')

    app=QtGui.QApplication(sys.argv)
    wideget=QtGui.QWidget()
    wideget.resize(250,150)
    wideget.setWindowTitle('simple')
    wideget.show()
    sys.exit(app.exec_())

def showRRG_M():
    app=QtGui.QApplication(sys.argv)
    rrg=RRG_M()
    rrg.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    showRRG_M()
