from PyQt4 import QtGui,QtCore
import pandas,indicator


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
