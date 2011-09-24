#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module implementing NetEditor's MainWindow.
"""
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import pyqtSignature

from Ui_neteditor import Ui_MainWindow
from data_io import  loadData
import networkx as nx
#import dgraph
import math
from math import sin,cos,pi
from numpy import array
import elasticnodes as dgraph
from multiprocessing import Process

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.network = None
        self.Map = None
        self.filename = None
    
    @pyqtSignature("QPoint")
    def on_centralWidget_customContextMenuRequested(self, pos):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("QPoint")
    def on_graphicsView_customContextMenuRequested(self, pos):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("QPoint")
    def on_edgeTable_customContextMenuRequested(self, pos):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        pass
    
    @pyqtSignature("")
    def on_edgeTable_itemSelectionChanged(self):
        """
        Slot documentation goes here.
        """
        pass
    
    @pyqtSignature("int, int")
    def on_edgeTable_cellDoubleClicked(self, row, column):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        pass
    
    @pyqtSignature("int, int")
    def on_edgeTable_cellActivated(self, row, column):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        pass
    
    @pyqtSignature("QPoint")
    def on_nodeTable_customContextMenuRequested(self, pos):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("QTableWidgetItem*")
    def on_nodeTable_itemActivated(self, item):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_nodeTable_itemSelectionChanged(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("int, int")
    def on_nodeTable_cellActivated(self, row, column):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("QAction*")
    def on_toolBar_actionTriggered(self, action):
        """
        Slot documentation goes here.
        """
        pass
    
    @pyqtSignature("")
    def on_actionOpen_edges_file_activated(self):
        """
        Slot documentation goes here.
        """
        fname = str(QtGui.QFileDialog.getOpenFileName(\
            None,
            self.trUtf8("Select an Epigrass edges file"),
            self.trUtf8("."),
            self.trUtf8("*.csv;;*.*"),
            None))
        self.filename = fname
        self.network = Network(self.graphicsView)
        edgelist = loadData(fname, ',')
        nodelist  = set([])
        header = edgelist.pop(0)
        
        self.edgeTable.setColumnCount(len(header))
        self.edgeTable.setRowCount(len(edgelist))
        self.edgeTable.setHorizontalHeaderLabels(header)
        print self.edgeTable.rowCount()
        for i,e in enumerate(edgelist):
            nodelist.add(e[5])
            nodelist.add(e[6])
            self.network.G.add_edge(e[5], e[6], {'weight':e[2], 'source_name':e[0], 'dest_name':e[1]}) #edge weight is flow S->D
            for j,v in enumerate(e):
                item  = QtGui.QTableWidgetItem(v)
                self.edgeTable.setItem(i,j,item)
        print self.edgeTable.takeItem(0,0).text()
        # Fill nodes table
        self.nodeTable.setColumnCount(1)
        self.nodeTable.setRowCount(len(nodelist))
        self.nodeTable.setHorizontalHeaderLabels(['Geocode'])
        for i,n in enumerate(nodelist):
            item = QtGui.QTableWidgetItem(n)
            self.nodeTable.setItem(i,0,item)
                
    
    @pyqtSignature("")
    def on_actionOpen_Shapefile_activated(self):
        """
        Slot documentation goes here.
        """
        fname = str(QtGui.QFileDialog.getOpenFileName(\
            None,
            self.trUtf8("Select a Shapefile"),
            self.trUtf8("."),
            self.trUtf8("*.shp"),
            None))
    
    @pyqtSignature("")
    def on_action_Save_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_actionSave_as_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_action_Graph_activated(self):
        """
        Draws the graph it there is a network loaded
        """
        if  self.network:
            nlist = []
            for k, v in self.network.getLayout().iteritems():
                nlist.append((k, v[0]*100, v[1]*100, str(k)))
            self.network.drawGraph(nlist, self.network.G.edges())
            
    
    @pyqtSignature("")
    def on_actionE_xit_activated(self):
        """
        Closes the network editor main window
        """
        self.close()
    
    @pyqtSignature("")
    def on_actionStats_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_actionCheck_Graph_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_actionDot_activated(self):
        """
        Slot documentation goes here.
        """
        if self.network:
            nx.write_dot(self.network.G, self.filename.split('.')[0]+'.dot')
    
    @pyqtSignature("")
    def on_actionGML_activated(self):
        """
        Slot documentation goes here.
        """
        if self.network:
            nx.write_gml(self.network.G, self.filename.split('.')[0]+'.gml')
    
    @pyqtSignature("")
    def on_actionPajek_activated(self):
        """
        Slot documentation goes here.
        """
        if self.network:
            nx.write_pajek(self.network.G, self.filename.split('.')[0]+'.pajek')
    
    @pyqtSignature("")
    def on_actionYAML_activated(self):
        """
        Slot documentation goes here.
        """
        if self.network:
            nx.write_yaml(self.network.G, self.filename.split('.')[0]+'.yaml')
    
    @pyqtSignature("")
    def on_action_Close_activated(self):
        """
        Slot documentation goes here.
        """
        self.edgeTable.clearContents()
        self.nodeTable.clearContents()
        self.network = None
        
class Network(object):
    '''
    This class handle every network related
    methods, from analysis  to drawing.
    '''
    def __init__(self, displaywidget):
        self.View = displaywidget
        self.View.scene = QtGui.QGraphicsScene(self.View)
        self.View.scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        self.N = Graph()
        self.G = nx.DiGraph(multiedges=True)
        self.timer = QtCore.QTimer()
        self.timerId = 0
        QtCore.QObject.connect(self.timer,QtCore.SIGNAL("timeout()"),self.timerEvent)


    def getLayout(self):
        return nx.random_layout(self.G)
        
    def timerEvent(self):
        print "event"
        nodes = [item for item in self.View.scene.items() if isinstance(item, Node)]
        for node in nodes:
            lw = LayoutWorker(node)
            lw.render()
#            node.calculateForces()

        itemsMoved = False
        for node in nodes:
            if node.advance():
                itemsMoved = True

        if not itemsMoved:
            self.centerScene()
            self.timer.stop()
            self.timerId = 0

    def drawGraph(self, nlist, elist):
        '''
        Draws Graph object representing the network
        '''
        npos= [(n[1], -n[2]) for n in nlist]
        xmin,ymin = array(npos).min(axis=0)
        xmax,ymax = array(npos).max(axis=0)
        for n in nlist:
            node = Node(self, n[0], n[3], self.View.scene)
            node.setPos(*(n[1], -n[2]))
            node.size = max(xmax-xmin, ymax-ymin)/math.sqrt(len(nlist))*0.5
            self.View.scene.addItem(node)
            self.N.insertNode(node)
            #print node.x(), node.y(), n.center[0], n.center[1]
        self.View.nodes = self.N.nodes
       
        asz = max(xmax-xmin, ymax-ymin)/math.sqrt(len(nlist))*0.2 #arrow size
        for e in elist:
            ed = Edge(self.N.polyDict[e[0]], self.N.polyDict[e[1]])
            ed.arrowSize = asz
            self.View.scene.addItem(ed)
            self.N.insertEdge(ed)
        self.xmax, self.xmin = xmax, xmin
        self.ymax, self.ymin = ymax, ymin
        self.centerScene()
        self.timerId = self.timer.start(200)
    

            
    def scaleView(self, scaleFactor):
        factor = self.View.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()

        if factor < 0.07 or factor > 100:
            return

        self.scale(scaleFactor, scaleFactor)
    

    def centerScene(self):
        """
        centers the scene and fits the specified rectangle to it
        """
#        ymax, ymin = self.ymax, self.ymin
#        xmax, xmin = self.xmax, self.xmin
        xmin, ymin, xmax, ymax = self.N.getRect()
        xxs = (xmax-xmin)*1.1 #percentage of extra space
        yxs = (ymax-ymin)*1.1 #percentage of extra space
        #calculating center of scene

        xc = (xmax+xmin)/2. 
        yc = (ymax+ymin)/2.
        self.View.scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        self.View.scene.setSceneRect(xmin, ymin, xxs, yxs)
#        print self.mapView.scene.width(), self.mapView.scene.height()
        self.View.fitInView(xmin, ymin, xxs, yxs)
        self.View.setScene(self.View.scene)
        self.View.updateSceneRect(self.View.scene.sceneRect())
        self.View.centerOn(xc, yc)
        scale_factor = self.View.width()/xxs
        self.View.scale(scale_factor, scale_factor)
        
        self.View.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.View.setRenderHint(QtGui.QPainter.Antialiasing)
        self.View.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.View.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        
class Graph(object):
    """
    The Graph.self.data(start)[5]
    """
    def __init__(self, **keywords):
        """
        Construct a Graph.
        """
        self.map = None
        self.nodes = []
        self.edges = []
        self.dragObject = None
        self.click = None
        self.distance = None
        self.timelabel = None
        self.rememberFixed = None
        self.rememberColor = None
#        self.display = display
        self.polyDict = {}#dictionary of nodes by geocode
        self.rect = [0,0,0,0]#xmin,ymin,xmax,ymax

    def insertNode(self, node):
        """
        Insert node into the system.
\        """
        #needs to be a list because the node index in this list identify it within the graph.

        #FIXME: verify time overhead of this check
        if not node in self.nodes:
            self.nodes.append(node)
            self.polyDict[node.geocode] = node
            node.graph = self #pass a reference of self to the node.

    def insertMap(self,map_):
        """
        Insert map into the system.
        """
        self.map = map_
        map_.graph = self

    def insertNodeList(self, nodelist):
        """
        Insert all Nodes in nodelist into the system.
        """

        map(self.insertNode, nodelist)

    def insertEdge(self, edge):
        """
        Insert edge into the system.
        """
        if edge not in self.edges:
            self.edges.append(edge)

    def insertEdgeList(self, edgelist):
        """
        Insert all Edges in edgelist into the system.
        """
        map(self.insertEdge, edgelist)

    def getEdgeFromMatrix(self, matrix):
        """
        Extract edges from the adjacency matrix.
        """
        #FIXME: eitehr integrate this into the graph object, or make it a separate function
        siz = matrix.shape[0]
        el = []
        for c in xrange(siz):
            for l in xrange(c+1): #scans only the lower triangle
                if matrix[l,c]:
                    el.append((c,l))
        return el


    def centerView(self):
        pass

    def getRect(self):
        '''
        Returns the bounding rectangle for the graph
        '''
        for n in self.nodes:
            self.rect[0] = n.x() if n.x() < self.rect[0] else self.rect[0]
            self.rect[1] = n.y() if n.y() < self.rect[1] else self.rect[1]
            self.rect[2] = n.x() if n.x() > self.rect[2] else self.rect[2]
            self.rect[3] = n.y() if n.y() > self.rect[3] else self.rect[3]
        return self.rect


class Node(QtGui.QGraphicsItem):
    Type = QtGui.QGraphicsItem.UserType + 1

    def __init__(self, network, geocode, name, scene):
        QtGui.QGraphicsItem.__init__(self)

        self.net = network
        self.scene = scene
        self.edgeList = []
        self.newPos = QtCore.QPointF()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)
        self.setZValue(1)
        self.geocode = geocode
        self.name = name
        self.size  = 10
        self.timerId = None
        

    def type(self):
        return Node.Type

    def addEdge(self, edge):
        self.edgeList.append(edge)
        edge.adjust()

    def edges(self):
        return self.edgeList

    def calculateForces(self):
        if not self.scene or self.scene.mouseGrabberItem() is self:
            self.newPos = self.pos()
            return
    
        # Sum up all forces pushing this item away.
        xvel = 0.0
        yvel = 0.0
        for item in self.scene.items():
            if not isinstance(item, Node):
                continue

            line = QtCore.QLineF(self.mapFromItem(item, 0, 0),
                    QtCore.QPointF(0, 0))
            dx = line.dx()
            dy = line.dy()
            l = 2.0 * (dx * dx + dy * dy)
            if l > 0:
                xvel += (dx * 150.0) / l
                yvel += (dy * 150.0) / l

        # Now subtract all forces pulling items together.
        weight = (len(self.edgeList) + 1) * 10.0
        for edge in self.edgeList:
            if edge.sourceNode() is self:
                pos = self.mapFromItem(edge.destNode(), 0, 0)
            else:
                pos = self.mapFromItem(edge.sourceNode(), 0, 0)
            xvel += pos.x() / weight
            yvel += pos.y() / weight
    
        if QtCore.qAbs(xvel) < 0.1 and QtCore.qAbs(yvel) < 0.1:
            xvel = yvel = 0.0

        sceneRect = self.scene.sceneRect()
        self.newPos = self.pos() + QtCore.QPointF(xvel, yvel)
        self.newPos.setX(min(max(self.newPos.x(), sceneRect.left() + self.size/2.), sceneRect.right() - self.size/2.))
        self.newPos.setY(min(max(self.newPos.y(), sceneRect.top() + self.size/2.), sceneRect.bottom() - self.size/2.))

    def advance(self):
        if self.newPos == self.pos():
            return False

        self.setPos(self.newPos)
        return True
        
    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionHasChanged:
            for edge in self.edgeList:
                edge.adjust()
            self.itemMoved()

        return super(Node, self).itemChange(change, value)
        
    def itemMoved(self):
        if not self.timerId:
            self.timerId = self.net.timer.start(200)



    def boundingRect(self):
        adjust = 2.0
        return QtCore.QRectF(-self.size/2. - adjust, -self.size/2. - adjust,
                             self.size*1.1 + adjust, self.size*1.1 + adjust)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(-self.size/2., -self.size/2., self.size,self.size)
        return path

    def paint(self, painter, option, widget):
#       Draw shadow
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.darkGray)
        painter.drawEllipse(-self.size/2., -self.size/2., self.size, self.size)

        gradient = QtGui.QRadialGradient(-self.size/6., -self.size/6., self.size/2.)
        if option.state & QtGui.QStyle.State_Sunken:
            gradient.setCenter(3, 3)
            gradient.setFocalPoint(3, 3)
            gradient.setColorAt(1, QtGui.QColor(QtCore.Qt.yellow).light(120))
            gradient.setColorAt(0, QtGui.QColor(QtCore.Qt.darkYellow).light(120))
        else:
            gradient.setColorAt(0, QtCore.Qt.yellow)
            gradient.setColorAt(1, QtCore.Qt.darkYellow)

        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 0))
        painter.drawEllipse(-self.size/2., -self.size/2., self.size,self.size)

#        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event):
        self.update()
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.update()
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

class Edge(QtGui.QGraphicsItem):
    Pi = math.pi
    TwoPi = 2.0 * Pi

    Type = QtGui.QGraphicsItem.UserType + 2

    def __init__(self, sourceNode, destNode):
        QtGui.QGraphicsItem.__init__(self)
        self.arrowSize = destNode.size/2.
        self.sourcePoint = QtCore.QPointF()
        self.destPoint = QtCore.QPointF()
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self.source = sourceNode
        self.dest = destNode
        self.source.addEdge(self)
        self.dest.addEdge(self)
        self.adjust()

    def type(self):
        return Edge.Type

    def sourceNode(self):
        return self.source

    def setSourceNode(self, node):
        self.source = node
        self.adjust()

    def destNode(self):
        return self.dest

    def setDestNode(self, node):
        self.dest = node
        self.adjust()

    def adjust(self):
        if not self.source or not self.dest:
            return

        line = QtCore.QLineF(self.mapFromItem(self.source, 0, 0),
                self.mapFromItem(self.dest, 0, 0))
        length = line.length()

        self.prepareGeometryChange()

        if length > self.dest.size:
            edgeOffset = QtCore.QPointF((line.dx() * self.source.size/.2) / length,
                    (line.dy() * self.dest.size/.2) / length)

            self.sourcePoint = line.p1() + edgeOffset
            self.destPoint = line.p2() - edgeOffset
        else:
            self.sourcePoint = line.p1()
            self.destPoint = line.p1()

    def boundingRect(self):
        if not self.source or not self.dest:
            return QtCore.QRectF()

        penWidth = 1
        extra = (penWidth + self.arrowSize) / 2.0

        return QtCore.QRectF(self.sourcePoint,
                             QtCore.QSizeF(self.destPoint.x() - self.sourcePoint.x(),
                                           self.destPoint.y() - self.sourcePoint.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def paint(self, painter, option, widget):
        if not self.source or not self.dest:
            return

        # Draw the line itself.
        line = QtCore.QLineF(self.sourcePoint, self.destPoint)

        if line.length() == 0.0:
            return

        painter.setPen(QtGui.QPen(QtCore.Qt.gray, .1, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawLine(line)

        # Draw the arrows if there's enough room.
        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = Edge.TwoPi - angle

        sourceArrowP1 = self.sourcePoint + QtCore.QPointF(sin(angle + pi / 3) * self.arrowSize,
                                                          cos(angle + pi / 3) * self.arrowSize)
        sourceArrowP2 = self.sourcePoint + QtCore.QPointF(sin(angle + pi - pi / 3) * self.arrowSize,
                                                          cos(angle + pi - pi / 3) * self.arrowSize);
        destArrowP1 = self.destPoint + QtCore.QPointF(sin(angle - pi / 3) * self.arrowSize,
                                                      cos(angle - pi / 3) * self.arrowSize)
        destArrowP2 = self.destPoint + QtCore.QPointF(sin(angle - pi + pi / 3) * self.arrowSize,
                                                      cos(angle - pi + pi / 3) * self.arrowSize)

        painter.setBrush(QtCore.Qt.gray)
        painter.drawPolygon(QtGui.QPolygonF([line.p1(), sourceArrowP1, sourceArrowP2]))
        painter.drawPolygon(QtGui.QPolygonF([line.p2(), destArrowP1, destArrowP2]))

class LayoutWorker(QtCore.QThread):
    def __init__(self,node,parent=None):
        QtCore.QThread.__init__(self, parent)
        self.mutex = QtCore.QMutex()
        self.node = node
        
    def __del__(self):
        pass
#        self.wait()
    def render(self):
        locker = QtCore.QMutexLocker(self.mutex)
        self.start()
    def run(self):
        self.node.calculateForces()


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    QtCore.qsrand(QtCore.QTime(0,0,0).secsTo(QtCore.QTime.currentTime()))
    MainW= QtGui.QMainWindow()
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
    

