__author__ = 'CaiMeng'

import sys,pandas,time
import EconomicData
from PyQt4 import QtGui,QtCore
import HKStock,indicator

class StockChart(QtGui.QMainWindow):

    xRay=[]

    # basicGraph to confirm the X axis
    # MainGraph=[]

    YR={}

    # numbers to adjust Y axis of each graph
    ymodify={}

    # data to be shown in the graph
    ShownGraph=[]

    GHights=[]

    # all data to be drawn
    Graph=[]

    alphaX=0.5

    # points data to be shown in the graph
    Points={}

    # lines to be drawn
    Line={}

    # candles to be drawn
    Candle={}

    # default color
    colors=[
        QtGui.QColor('cyan'),
        QtGui.QColor('white'),
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
    xSize=30
    ySize=50

    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)

        self.xCounts=(int)(self.width()*self.alphaX)
        self.command={
            QtCore.Qt.Key_Down:self.down,
            QtCore.Qt.Key_Up:self.up
            }
        # print(self.Data['tradeDate'])

        self.initWidget()
        # self.setToolTip('widget')
        # self.initBottoms()

    def importLine(self,name=None,line=None,figure=0,color=None):

        while len(self.Graph)<=figure:
            self.Graph.append({'line':{}})
            self.ShownGraph.append({'line':{}})


        if name is None:
            name='Line%s' % len(self.Graph[figure]['line'])

        if color is not None:
            self.chartColor[name]=color
        else:
            self.chartColor[name]=self.colors[len(self.Graph[figure]['line'])]

        self.Graph[figure]['line'][name]=line

        def outXRay(x):
            return x not in self.xRay

        outxray=list(filter(outXRay,line[0]))
        if len(outxray)>0:
            self.xRay.extend(outxray)
            self.xRay.sort()



    def importCandle(self,name=None,candle=None,figure=0,color=None,main=False):
        while len(self.Graph)<=figure:
            self.Graph.append({'candle':{}})


        if name is None:
            name='Candle%s' % len(self.Graph[figure]['candle'])

        self.Graph[figure]['candle'][name]=candle

        pass

    def down(self):
        self.alphaX*=0.8
        self.repaint()
        print('down',self.xCounts)

    def up(self):
        self.alphaX/=0.8
        self.repaint()
        print('up',self.xCounts)

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
            self.GHights.append(1/(1+len(self.Graph))*self.height())

        # self.setdefaultChartColor()

        self.xCounts=(int)(self.width()*self.alphaX)

        self.defineRange()
        R=self.Xrange()
        self.XR=R[0:2]

        self.Range=R

        qp=QtGui.QPainter()
        qp.begin(self)
        qp.save()

        self.xmodify=(R[0]-R[1])/self.areaWidth

        for f in range(0,len(self.Graph)):

            self.drawGraph(event,qp,f,height=self.GHights[f])

        qp.translate(0,-self.xSize)
        self.drawXaxis(event,qp)

        qp.restore()
        qp.end()

    def drawGraph(self,event,qp,num,height):

        qp.restore()
        qp.save()

        startY=0
        for n in range(0,num):
            startY=startY+self.GHights[n]
        self.drawBackGround(event,qp,QtCore.QRect(0,startY,self.width(),height))

        self.drawLabel(event,qp,num,y=startY)

        # draw outlines
        qp.setPen(QtGui.QColor(255,255,255))
        qp.drawLine(QtCore.QPoint(0,startY),QtCore.QPoint(self.width(),startY))
        qp.drawLine(QtCore.QPoint(self.areaWidth,startY),QtCore.QPoint(self.areaWidth,startY+self.GHights[num]))

        qp.scale(1,-1)
        qp.translate(0,-startY-height)

        YR=self.Yrange(num)

        self.YR[num]=YR
        print(self.YR)
        # print(self.Line.keys())
        self.ymodify[num]=(YR[0]-YR[1])/height
        self.drawLines(event,qp,num=num)

    def drawXaxis(self,event,qp):
        self.drawBackGround(event,qp,QtCore.QRect(0,0,self.width(),self.xSize))
        qp.setPen(QtGui.QColor(255,255,255))
        qp.drawLine(0,self.xSize,self.width(),self.xSize)

        font=QtGui.QFont('xAxis',self.xSize-2)
        qp.setFont(font)

        shown=[]
        for xa in self.xAxis:
            x=(xa-self.XR[1])/self.xmodify
            date=time.localtime(xa)
            date=time.strftime('%Y/%m/%d %H:%M',date)
            shown.append([x,date])

        print(shown)

        # pass


    def drawLabel(self,event,qp,num=0,size=12,y=0):
        c=2
        font=QtGui.QFont('label',size)
        font.setWeight(63)

        for ct in self.ShownGraph[num].values():
            for name in ct.keys():
                qp.setPen(self.chartColor[name])
                qp.setFont(font)

                qp.drawText(c,y+size+2,name)
                c=c+size*len(name)


    def Yrange(self,num):
        maxY=[]
        minY=[]

        g=self.ShownGraph[num]
        for type in g.keys():
            if type=='line':
                for name in g[type].keys():
                    maxY.append(max( g[type][name][1]))
                    minY.append(min( g[type][name][1]))

        return [max(maxY),min(minY)]



    def Xrange(self):

        self.xAxis=[]
        maxX=[]
        minX=[]
        for g in self.ShownGraph:
            for l in g.keys():
                if l == 'line':
                    for name in g[l].keys():
                        maxX.append(max(g[l][name][0]))
                        minX.append(min(g[l][name][0]))

                        self.xAxis=list(set(self.xAxis).union(g[l][name][0]))

        self.xAxis.sort()
        # print(self.xAxis)
        return [max(maxX),min(minX)]

    def defineRange(self):
        leftX=self.xRay[-self.xCounts]
        rightX=self.xRay[-1]
        # print('left:%s,right%s' % (leftX,rightX))
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

        XLine={}
        gn=0

        for g in self.Graph:
            for l in g.keys():
                if l == 'line':
                    for name in g[l].keys():
                        xrange=xRange(g[l][name][0],leftX,rightX)
                        XLine[name]=[
                            g[l][name][0][xrange[0]:xrange[1]],
                            g[l][name][1][xrange[0]:xrange[1]]
                        ]
                        print('definerange',len(XLine[name][0]))

            self.ShownGraph[gn]['line']=XLine
            XLine={}
            gn=gn+1



    def wheelEvent(self, event):
        # print(event.delta())
        if event.delta()>0:
            self.up()
        else:
            self.down()

    def mousePressEvent(self, event):
        x=event.x()
        print(x)

    def mouseMoveEvent(self, event):
        x=event.x()
        y=event.y()
        print(x,y)

    def keyPressEvent(self, event):


        if event.key() in self.command.keys():
            print((event.key()))
            self.command[event.key()]()


    def drawLines(self,event,qp,num=0):
        self.Line=self.ShownGraph[num]['line']

        c=0

        # k: name of each Line
        for k in self.Line.keys():

            v=self.Line[k]
            points=[]


            x,y=0,0


            self.Points[k]={'x':[],'y':[]}
            for i in range(0,len(v[0])):
                x=(v[0][i]-self.XR[1])/self.xmodify
                y=(v[1][i]-self.YR[num][1])/self.ymodify[num]

                points.append(QtCore.QPointF(x,y))
                self.Points[k]['x'].append(x)
                self.Points[k]['y'].append(y)


            # print(k,self.Points[k]['x'][0:10])
            # print(k,self.ShownGraph[num]['line'][k][1][0:10])
            qp.setPen(self.chartColor[k])
            for p in range(1,len(points)):
                qp.drawLine(points[p-1],points[p])


    def drawSquare(self,event,qp):
        color=QtGui.QColor(255,255,255)
        qp.setBrush(color)
        qp.drawRect(20,20,10,30)



    def drawCandle(self,event,qp,candle):
        color=QtGui.QColor(255,255,255)
        qp.setBrush(color)
        qp.drawRect(candle[0]+10+4,candle[3]+10,2,candle[2]-candle[3])
        qp.drawRect(candle[0]+10,candle[1]+10,10,candle[4]-candle[1])



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



def printData():
    print(EconomicData.getYahooData())

def showChart():
    app=QtGui.QApplication(sys.argv)
    window=StockChart()

    HSI=pandas.read_excel('%s.xlsx' % HKStock.HKindex[0])
    date=[]
    for d in HSI.tradeDate:
        date.append(time.mktime(time.strptime(d,'%Y-%m-%d')))
    window.importLine(name=HKStock.HKindex[0],line=[
        date,HSI.closeIndex.tolist()
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



if __name__ == '__main__':

    showChart()
