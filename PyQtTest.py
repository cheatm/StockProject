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
    xSize=20
    ySize=50

    # supportLines
    extraLines=[]

    # extra y label to draw
    yLabel={}

    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)

        self.xCounts=(int)(self.width()*self.alphaX)
        self.command={
            QtCore.Qt.Key_Down:self.down,
            QtCore.Qt.Key_Up:self.up
            }
        # print(self.Data['tradeDate'])
        self.BGcolor= QtGui.QColor(0,0,0)
        self.initWidget()
        # self.setToolTip('widget')
        # self.initBottoms()

    def importLine(self,name=None,line=None,figure=0,color=None,**args):

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

        for s in args.keys():

            pass

    def importCandle(self,name=None,candle=None,figure=0,color=None,main=False):
        while len(self.Graph)<=figure:
            self.Graph.append({'candle':{}})
            self.ShownGraph.append({'candle':{}})


        if name is None:
            name='Candle%s' % len(self.Graph[figure]['candle'])

        if color is not None:
            self.chartColor[name]=color
        else:
            self.chartColor[name]=self.colors[len(self.Graph[figure]['candle'])]

        self.Graph[figure]['candle'][name]=candle

        # print(self.Graph[figure]['candle'][name])

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
            qp.drawText(self.posx,self.height()-textSize/3,date)

            # gap=self.areaWidth/len(self.shownX)/2
            # for t in self.shownX.keys():
            #     if abs(self.posx-self.shownX[t])<=gap:
            #         date=self.toStrDate(t)
            #         self.crossLineX=date
            #         qp.drawText(self.posx,self.height()-textSize/3,date)
            #
            #         break

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

        # self.drawLabel(event,qp,num,y=startY)

        # draw outlines
        qp.setPen(QtGui.QColor(255,255,255))
        qp.drawLine(QtCore.QPoint(0,startY),QtCore.QPoint(self.width(),startY))
        qp.drawLine(QtCore.QPoint(self.areaWidth,startY),QtCore.QPoint(self.areaWidth,startY+self.GHights[num]))

        qp.scale(1,-1)
        qp.translate(0,-startY-height)

        YR=self.Yrange(num)

        self.YR[num]=YR
        # print('YR : ',self.YR)

        self.ymodify[num]=(YR[0]-YR[1])/height

        # draw charts
        self.drawLines(event,qp,num)
        self.drawCandles(event,qp,num)

        qp.scale(1,-1)

        self.drawYaxis(event,qp,num)

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

    def setYlabel(self,value=None,count=None,num=0,):
        if value is not None:
            if num not in self.yLabel.keys():
                self.yLabel[num]=[value]
            else:
                self.yLabel[num].append(value)

        if count is not None:
            if num not in self.yLnumber.keys():
                self.yLnumber[num]=count
            else:
                self.yLnumber[num]=count

    def drawYaxis(self,event,qp,num=0,lines=2):
        R=self.YR[num][0]-self.YR[num][1]

        textSize=self.xSize*3/5
        font=QtGui.QFont('yAxis',textSize)
        qp.setFont(font)
        qp.setPen(QtGui.QColor(255,255,255))

        if num in self.yLabel.keys():
            for value in self.yLabel[num]:
                y=-(value-self.YR[num][1])/self.ymodify[num]
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
                if value in lis:
                    return (lis.index(value))
            return (-1)

        for ct in self.ShownGraph[num].values():
            for name in ct.keys():
                qp.setPen(self.chartColor[name])
                qp.setFont(font)

                label="%s:" % name

                for v in ct[name][1:]:
                    label=label+str(v[ findIndex(ct[name][0],x) ])+" "
                    # print(x)
                # print(label)

                # label="%s:%s" % (name,ct[name][-1][-1])
                qp.drawText(c,y+size+2,label)
                c=c+size*len(label)*4/5



    def Yrange(self,num):
        maxY=[]
        minY=[]

        g=self.ShownGraph[num]
        for type in g.keys():

            if type=='line':
                for name in g[type].keys():
                    maxY.append(max( g[type][name][1]))
                    minY.append(min( g[type][name][1]))
            if type=='candle':
                # print(type)
                for name in g[type].keys():
                    maxY.append(max( g[type][name][2]))
                    minY.append(min( g[type][name][3]))
                    # print(maxY)

        return [max(maxY),min(minY)]


    def defineRange(self):
        if self.xCounts>len(self.xRay):
            self.xCounts=len(self.xRay)
        leftX=self.xRay[-self.xCounts]
        rightX=self.xRay[-1]
        self.XR=[rightX,leftX]
        self.xmodify=(rightX-leftX)/self.areaWidth

        shownXray=self.xRay[-self.xCounts:-1]
        self.shownX={}
        for x in range(0,len(shownXray)):
            self.shownX[shownXray[x]]=(x+0.5)*self.areaWidth/len(shownXray)
            pass

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
            # print((event.key()))
            self.command[event.key()]()


    def drawCandles(self,event,qp,num=0):

        if 'candle' not in self.ShownGraph[num].keys():
            return (None)

        candle=self.ShownGraph[num]['candle']

        for k in candle.keys():
            v=candle[k]
            candlewidth=self.areaWidth/len(v[0])*0.9
            qp.setPen(self.chartColor[k])

            for i in range(0,len(v[0])):
                single=[self.shownX[v[0][i]]]
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
            points=[]

            x,y=0,0

            self.Points[k]={'x':[],'y':[]}
            for i in range(0,len(v[0])):
                x=self.shownX[v[0][i]]
                # x=(v[0][i]-self.XR[1])/self.xmodify
                y=(v[1][i]-self.YR[num][1])/self.ymodify[num]

                points.append(QtCore.QPointF(x,y))
                self.Points[k]['x'].append(x)
                self.Points[k]['y'].append(y)

            qp.setPen(self.chartColor[k])
            for p in range(1,len(points)):
                qp.drawLine(points[p-1],points[p])


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



def printData():
    print(EconomicData.getYahooData())

def showChart():
    app=QtGui.QApplication(sys.argv)
    window=StockChart()

    HSI=pandas.read_excel('%s.xlsx' % HKStock.HKindex[0])
    date=[]
    for d in HSI.tradeDate:
        date.append(time.mktime(time.strptime(d,'%Y-%m-%d')))
    # window.importLine(name=HKStock.HKindex[0],line=[
    #     date,HSI.closeIndex.tolist()
    # ])
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



if __name__ == '__main__':

    showChart()
