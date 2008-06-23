#! /usr/bin/env python
"""
This module is a graph visualizing tool.
It tries to resolves the graph layout by making an analogy
of the nodes and edges to masses and springs.
the nodes repel each other with a force inversely proportional to their
distance, and the edges do the opposite.
"""
import math, ogr
import threading
#from numpy import *
#import visual 
import time, os,  sys
from PyQt4 import Qt, QtCore, QtGui, QtOpenGL, Qwt5 as Qwt
from numpy import  array, sqrt,  average
from numpy.random import randint, uniform
from Ui_display import Ui_Form 
#from pylab import *
from matplotlib import cm
from types import MethodType
from SimpleXMLRPCServer import SimpleXMLRPCServer
##import psyco
##psyco.full()

graphic_backend = "qt"



def keyPressEvent(self, event):
    key = event.key()
    if key == QtCore.Qt.Key_Up:
        self.translate(0, -20)
    elif key == QtCore.Qt.Key_Down:
        self.translate(0, 20)
    elif key == QtCore.Qt.Key_Left:
        self.translate(-20, 0)
    elif key == QtCore.Qt.Key_Right:
        self.translate(20, 0)
    elif key == QtCore.Qt.Key_Plus:
        self.scaleView(1.2)
    elif key == QtCore.Qt.Key_Minus:
        self.scaleView(1 / 1.2)
    elif key == QtCore.Qt.Key_Space or key == QtCore.Qt.Key_Enter:
        for item in self.scene().items():
            if isinstance(item, Polygon):
                item.setPos(-150 + QtCore.qrand() % 300, -150 + QtCore.qrand() % 300)
    else:
        QtGui.QGraphicsView.keyPressEvent(self, event)


def wheelEvent(self, event):
    self.scaleView(math.pow(2.0, -event.delta() / 240.0))
    
def scaleView(self, scaleFactor):
    factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
#        if factor < 0.07 or factor > 1000000:
#            return
    self.scale(scaleFactor, scaleFactor)

def array_mag(a):
    acc = 0
    for value in a:
        acc += value ** 2
    return math.sqrt(acc)

def array_norm(a):
    """normalizes an array"""
    mag = array_mag(a)
    b = a.copy()
    for i in xrange(len(a)):
        b[i] = b[i] / mag
    return b
def array_dot(a,b):
    return sum([a[i] * b[i]  for i in xrange(len(a))])
#TODO: implement the replay button
class MapWindow(Ui_Form):
    '''
    Map and Time-series window
    '''
    def __init__(self, G=None):
        self.Form =  QtGui.QWidget()
        self.setupUi(self.Form)
        self.jet  = cm.get_cmap("jet",50) #colormap
        self.timeseries = {}
        self.setupQwtPlot()
        self.step = 0
        self.M = None #initialize map
        # Overloading event-handling methods for self.mapView
        self.mapView.keyPressEvent = MethodType(keyPressEvent, self.mapView)
        self.mapView.wheelEvent = MethodType(wheelEvent, self.mapView)
        self.mapView.scaleView = MethodType(scaleView, self.mapView)
        # connections
        QtCore.QObject.connect(self.horizontalSlider,QtCore.SIGNAL("sliderReleased()"), self.on_horizontalSlider_sliderMoved)
        QtCore.QObject.connect(self.horizontalSlider,QtCore.SIGNAL("valueChanged()"), self.on_horizontalSlider_valueChanged)
        self.server = MapServer()
#        self.server.map = self.M
        st = threading.Thread(target=self.server.start)
        st.start()
        
    def setupQwtPlot(self):
        """
        sets up the time series plot
        """
        #TODO: Adjust font size for the whole plot
        #TODO: change colors for each plot
        
        self.qwtPlot.setTitle('Simulation Time Series')
        self.qwtPlot.setAxisTitle(Qwt.QwtPlot.xBottom, 'time')
        self.qwtPlot.setAxisTitle(Qwt.QwtPlot.yLeft,  'count')
        self.qwtPlot.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.RightLegend)
        # Time marker
        self.mX = Qwt.QwtPlotMarker()
        self.mX.setLabel(Qwt.QwtText('current time'))
        self.mX.setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignTop)
        self.mX.setLineStyle(Qwt.QwtPlotMarker.VLine)
        self.mX.setXValue(0)
        self.mX.attach(self.qwtPlot)
        self.qwtPlot.replot()
    def addTsCurve(self, gc, name):
        """
        plots a time series curve to the plot window
        """
        data = [0]*len(self.timeseries)
        for k, v in self.timeseries.items():
            data[k] = v[gc]
        t = self.timeseries.keys()
        t.sort()
        curve = Qwt.QwtPlotCurve(name)
        curve.setPen(Qt.QPen(Qt.Qt.blue))
        curve.attach(self.qwtPlot)
        curve.setData(t, data)
        
    def drawMap(self, filename, namefield, geocfield):
        """
        Draws the map store in the shapefile fname.
        """
        #Setup the Map
        self.M = Map(fname=filename,display=self, namefield=namefield, geocfield=geocfield)
        self.server.map = self.M
        xmin,ymin = self.M.xmin, self.M.ymin
        xmax,ymax = self.M.xmax, self.M.ymax
        xxs = (xmax-xmin)*1.1 #percentage of extra space
        yxs = (ymax-ymin)*1.1 #percentage of extra space
        #calculating center of scene
#        FIXME: descobrir o que ha de diferente com a a centralizacao quando chamado do Epigrass 
        xc = (xmax+xmin)/2. 
        yc = (ymax+ymin)/2.
        self.mapView.scene = QtGui.QGraphicsScene(self.mapView)
        #self.mapView.scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        self.mapView.scene.setSceneRect(xmin, ymin, xxs, yxs)
        #print self.mapView.scene.width(), self.mapView.scene.height()
        self.mapView.fitInView(xmin, ymin, xxs, yxs)
        self.mapView.setScene(self.mapView.scene)
        self.mapView.updateSceneRect(self.mapView.scene.sceneRect())
        self.mapView.centerOn(xc, yc)
        
        #self.mapView.setViewport(QtOpenGL.QGLWidget())
        self.mapView.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.mapView.setRenderHint(QtGui.QPainter.Antialiasing)
        self.mapView.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.mapView.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        
        for p in self.M.polyList:
            self.mapView.scene.addItem(p)
        #self.scene.addText("%s,%s,%s,%s"%(xmin, xxs, ymin, yxs))
        self.polys = [item for item in self.mapView.scene.items() if isinstance(item, Polygon)]
        #self.mapView.addGraph(self.polys)
        self.mapView.setMinimumSize(400, 400)
        #self.mapView.setWindowTitle(self.tr("Network View"))
        scale_factor = self.mapView.width()/xxs
        self.mapView.scale(scale_factor, scale_factor)
        
        #print self.polys
    
    def addGraph(self, nlist, elist=[] ):
        G = Graph(self)
        for n in nlist:
            node = QtNode(1, n.center, display = self)
            #node.setPos(node.mapFromScene(QtCore.QPointF(node.x(), node.y())))
            self.mapView.scene.addItem(node)
            G.insertNode(node)
            #print node.x(), node.y(), n.center[0], n.center[1]
        self.scene.update()
    
    def paintPols(self, datadict):
        """
        Paint the polygons with the data from data dict
        datadict is a dictionary of the form {geocode:value,...}
        """
        if max(datadict.values()) > 1:
            normw = max(datadict.values())
        else:
            normw = 1
        for gc, val in datadict.iteritems():
            val /= normw #normalize values if necessary
            col = self.jet(val)#rgba list
            gc = int(gc)
#            print gc, type(gc)
            if self.M.polyDict.has_key(gc):
                self.M.polyDict[gc].fillColor = QtGui.QColor(int(col[0]*255), int(col[1]*255), int(col[2]*255), int(col[3]*255))
                self.M.polyDict[gc].update()
#            else:
#                print self.M.polyDict.values()
        
    def drawStep(self,step,  datadict={}):
        """
        Draws one timestep on the map
        step: timestep number
        datadict: dictionary geocode:value
        """
        self.step = step
        self.paintPols(datadict)
        self.lcdNumber.display(step)
        self.horizontalSlider.setValue(step)
        self.timeseries[step] = datadict

    def flashBorders(self,  gclist=[]):
        """
        Flash the borders to bright green to signal events
        gclist: list of geocodes to be flashed
        """
        for gc in gclist:
            gc = int(gc)
            self.M.polyDict[gc].lineColor = QtCore.Qt.green
            self.M.polyDict[gc].update()
        self.M.polyDict[gc].lineColor = QtCore.Qt.black
    
    def show(self):
        self.Form.show()

    def on_horizontalSlider_valueChanged(self):
        if self.horizontalSlider.isEnabled():
            self.on_horizontalSlider_sliderMoved()
    def on_horizontalSlider_sliderMoved(self):
        """
        Handles updating the display on a slider move
        """
        val = self.horizontalSlider.value()
        self.lcdNumber.display(val)
        self.step = val
        self.drawStep(val, self.timeseries[val])
        self.mX.setXValue(self.step)
        self.qwtPlot.replot()
        
#BlackBox  :-)
class BaseBox(object):
    def __init__(self, *args, **kwargs):
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])
BaseCylinder = BaseBox


#Short factory functions, so that callers don't have to care
#about which class is being used for visualization
def Node(*args, **kwargs):
    if graphic_backend == "visual":
        return VisualNode(*args, **kwargs)
    elif graphic_backend == "qt":
        return QtNode(*args, **kwargs)
    else:
        return BaseNode(*args, **kwargs)

def RubberEdge(*args, **kwargs):
    if graphic_backend == "visual":
        return VisualRubberEdge(*args, **kwargs)
    elif graphic_backend == "qt":
        return QtRubberEdge(*args, **kwargs)
    else:
        return BaseRubberEdge(*args, **kwargs)

def Graph(*args, **kwargs):
    if graphic_backend == "visual":
        return VisualGraph(*args, **kwargs)
    elif graphic_backend == "qt":
        return QtGraph(*args, **kwargs)
    else:
        return BaseGraph(*args, **kwargs)
def Map(*args, **kwargs):
    if graphic_backend == "visual":
        return VisualMap(*args, **kwargs)
    elif graphic_backend == "qt":
        return QtMap(*args, **kwargs)
    else:
        return BaseGraph(*args, **kwargs)

rho = 23.8732414637845 # for backwardscompatibility


class BaseNode(object):
    """
    Physical model of a node as a mass.
    """
    factor = 3. / (4 * math.pi * rho)

    def __init__(self, m, pos, r=.1, fixed=0, pickable=1, v=(0., 0., 0.), color=(0., 1., 0.), name='', **keywords):
        """
        Construct a mass.
        """
        if not r:
            # rho = m / V; V = 4 * PI * r^3 / 3
            r = math.pow(Node.factor * m, 1./3)
        self.r = r

        self.m = float(m)
        self.fixed = fixed
        self.pickable = pickable

        self.graph = None

        self.painted = 0
        self.name = name.encode('latin-1','replace')
        self.ts = []
        self.tsdone = 0 #true if time series has been plot

        try:
            self.geocode = keywords['geocode']
        except KeyError:
            self.geocode = None
        #this "array" comes from numpy
        #these properties  have to be defined in each subclass.
        # FIXME: maybe just "visual"  will need to redefine these in teh end.
        if self.__class__ == BaseNode:
            self.box = BaseBox(pos=array(pos),length=float(r),
                               height=r,width=r,color=color,
                               name='',**keywords)
        self.v = array(v)
        self.F = array((0., 0., 0.))
        self.pos = array(pos)

    def showName(self,t):
        """
        Show the node name for t seconds
        """
        pass

    def calcGravityForce(self, g):
        """
        Calculate the gravity force.
        """
        for n in self.graph.nodes:
            if not self==n:
                self.F -= (self.pos - n.pos)


    def calcViscosityForce(self, viscosity):
        """
        Calculate the viscosity force.
        """
        # Fviscosity = - v * viscosityFactor
        self.F -= self.v * viscosity

    def calcNewLocation(self, dt):
        """
        Calculate the new location of the mass.
        """
        # F = m * a = m * dv / dt  =>  dv = F * dt / m
        dv = self.F * dt / self.m
        self.v += dv
        # v = dx / dt  =>  dx = v * dt
        self.pos += self.v * dt
        self.box.pos += self.v * dt

    def clearForce(self):
        """
        Clear the Force.
        """
        self.F = array((0., 0., 0.))


class _BaseEdge(object):
    """
    Physical model of an edge as a spring.
    """

    def __init__(self, n0, n1, k, l0=None, damping=None):
        """
        Construct a spring edge.
        """
        self.n0 = n0
        self.n1 = n1
        self.k = k
        if l0:
            self.l0 = l0
        else:
            self.l0 = array_mag(self.n1.pos - self.n0.pos)
        self.damping = damping
        self.e = array((0., 0., 0.))

    def calcSpringForce(self):
        """
        Calculate the spring force.
        """
        delta = self.n1.box.pos - self.n0.box.pos
        l = array_mag(delta)
        self.e = array_norm(delta)
        # Fspring = (l - l0) * k
        Fspring = (l - self.l0) * self.k * self.e
        self.n0.F += Fspring
        self.n1.F -= Fspring

    def calcDampingForce(self):
        """
        Calculate the damping force.
        """
        # Fdamping = v in e * dampingFactor
        Fdamping = (array_dot((self.n1.v - self.n0.v), self.e) *
                    self.damping * self.e)
        self.n0.F += Fdamping
        self.n1.F -= Fdamping



class BaseRubberEdge(_BaseEdge):
    """
    Visual representation of a spring using a single cylinder with variable radius.
    """

    def __init__(self, n0, n1, k, l0=None, damping=None,
                 radius=None, color=(0.5,0.5,0.5), **keywords):
        """
        Construct a rubber spring.
        """
        _BaseEdge.__init__(self, n0, n1, k, l0, damping)
        if radius is None:
            radius = (self.n0.box.length + self.n1.box.length) * 0.1
        self.r0 = radius
        #these proeperties  have to be defined in each subclass.
        # FIXME: maybe just "visual"  will need to redefine these in the end.
        if self.__class__ == BaseNode:
            self.cylinder = BaseCylinder(pos=self.n0.box.pos,
                                         axis=self.n1.pos - self.n0.pos,
                                         radius=radius, color=color,
                                         **keywords)

    def update(self):
        """
        Update the visual representation of the spring.
        """
        self.cylinder.pos = self.n0.pos
        self.cylinder.axis = self.n1.pos - self.n0.pos




class BaseGraph(object):
    """
    The Graph.self.data(start)[5]
    """
    def __init__(self, timestep=0.04, oversample=1, gravity=1, viscosity=None, name='EpiGrass Viewer', **keywords):
        """
        Construct a Graph.
        """
        self.timestep = timestep
        self.rate = 1.0 / timestep
        self.oversample = oversample
        self.gravity = gravity
        self.viscosity = viscosity

        self.map = None

        self.nodes = []
        self.edges = []

        self.dragObject = None
        self.click = None
        self.distance = None
        self.timelabel = None
        self.rememberFixed = None
        self.rememberColor = None

        self.display = BaseBox()


    def addTimelabel(self):
        """
        Adds the time label at the center of the display
        """
        self.timelabel = "0"
        pass

    def insertNode(self, node):
        """
        Insert node into the system.
\        """
        #needs to be a list because the node index in this list identify it within the graph.

        #FIXME: verify time overhead of this check
        if not node in self.nodes:
            self.nodes.append(node)
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

    def advance(self):
        """
        Perform one Iteration of the system by advancing one timestep.
        """
        microstep = self.timestep / self.oversample
        center = visual.vector(0,0,0)
        for i in range(self.oversample):
            for edge in self.edges:
                edge.calcSpringForce()
                if edge.damping:
                    edge.calcDampingForce()

            for node in self.nodes:
                if not node.fixed:
                    if self.gravity:
                        node.calcGravityForce(self.gravity)
                    if self.viscosity:
                        node.calcViscosityForce(self.viscosity)
                    node.calcNewLocation(microstep)
                node.clearForce()
                center += node.pos
                self.center = center/float(len(self.nodes))
            for edge in self.edges:
                edge.update()

    def dispatchDnD(self):
        """Process the drag and drop interaction from the mouse.
        """
        pass


    def step(self):
        """Perform one step.  This is a convenience method.
        It actually calls dispatchDnD() and advance().
        """

        self.advance()
        time.sleep(self.timestep)

    def mainloop(self):
        """Start the mainloop, which means that step() is
        called in an infinite loop.
        """
        while 1:
            self.step()


class BaseMap(object):
    def __init__(self, fname,namefield='NOME_ZONAS',geocfield='ZONA_TRAFE'):
        self.namefield = namefield
        self.geocfield = geocfield
        self.centroids = []#centroid list (x,y,z) tuples
        self.centdict = {} #keys are geocode, values are (x,y,z) tuples
        self.geomdict = {} #keys are geocode, values are geometries
        self.nlist = []#nodelist: feature objects
        self.polyList = []#Qpolygon list: Polygon objects
        self.polyDict = {}
        if os.path.exists(fname):
            self.Reader(fname)
        else:
            print "shapefile %s not found in %s"%(fname, os.getcwd())


    def Reader(self, fname):
        """
        Reads shapefiles vector files.
        """
        g = ogr.Open (fname)
        L = g.GetLayer(0)
        N = 0
        tp = []
        feat = L.GetNextFeature()
        while feat is not None:
            field_count = L.GetLayerDefn().GetFieldCount()
            geo = feat.GetGeometryRef()
            if geo.GetGeometryCount()<2:
                g1 = geo.GetGeometryRef( 0 )
                geocode = feat.GetFieldAsInteger(self.geocfield)
                name = feat.GetFieldAsString(self.namefield)
                self.geomdict[geocode] = g1
                if g1.GetGeometryType() == 3: #If it is a polygon
                    cen = g1.Centroid()
                    self.nlist.append(feat)
                    self.centdict[geocode] = (cen.GetX(),cen.GetY(),cen.GetZ())
                x =[g1.GetX(i) for i in xrange(g1.GetPointCount()) ]
                y =[-g1.GetY(i) for i in xrange(g1.GetPointCount()) ]
                lp = zip(x,y)#list of points
                tp += lp
                #print geocode
                self.dbound(lp, geocode, name)
            for c in xrange( geo.GetGeometryCount()):
                ring = geo.GetGeometryRef ( c )
                for cnt in xrange(ring.GetGeometryCount()):
                    g1 = ring.GetGeometryRef( cnt )
                    if g1.GetGeometryType() == 3: #If it is a polygon
                        geocode = feat.GetFieldAsInteger(self.geocfield)
                        name = feat.GetFieldAsString(self.namefield)
                        self.geomdict[geocode] = g1
                        cen = g1.Centroid()
                        self.nlist.append(feat)
                        self.centdict[geocode] = (cen.GetX(),cen.GetY(),cen.GetZ())
                    x =[g1.GetX(i) for i in xrange(g1.GetPointCount()) ]
                    y =[-g1.GetY(i) for i in xrange(g1.GetPointCount()) ]
                    lp = zip(x,y)#list of points
                    tp += lp
#                    print geocode
                    self.dbound(lp, geocode,  name)
            feat = L.GetNextFeature()

        g.Destroy()
        tp = array(tp)
        self.dimension = tp.max()
        center = average(tp,axis=0)
        self.center = center

    def dbound(self, *args):
        pass



class QtMap(BaseMap):
    def __init__(self, fname, display=None, namefield='NOME_ZONAS',geocfield='ZONA_TRAFE'):
        self.display = display
        self.xmin, self.ymin, self.xmax,self.ymax = 180, 90, -180, -90
        BaseMap.__init__(self, fname,namefield,geocfield)
        
    def dbound(self, pol, geocode = None , name=""):
        #FIXME: consertar algoritmo para funcionar com qualquer sistema de coordenadas
        p = Polygon(pol, geocode,name,  self.display)
        self.xmin = p.xmin if p.xmin<self.xmin else self.xmin
        self.ymin = p.ymin if p.ymin<self.ymin else self.ymin
        self.xmax = p.xmax if p.xmax>self.xmax else self.xmax
        self.ymax = p.ymax if p.ymax>self.ymax else self.ymax
        #print self.xmin,  self.ymin,  self.xmax, self.ymax
        self.polyList.append(p)
        #print geocode
        self.polyDict[geocode] = p
        return p

class Polygon(QtGui.QGraphicsItem):
    '''
    Polygons that compose the map on Qt
    '''
    Type = QtGui.QGraphicsItem.UserType + 1
    def __init__(self,plist, geocode, name,   graphWidget):
        QtGui.QGraphicsItem.__init__(self)
        self.display = graphWidget
        self.xmin,self.ymin = (array(plist)).min(axis=0)
        self.xmax,self.ymax = (array(plist)).max(axis=0)
        self.center = ((self.xmax+self.xmin)/2., (self.ymax+self.ymin)/2.)
        self.width = self.xmax-self.xmin
        self.height = self.ymax-self.ymin
        self.plist = plist
        self.pointList = [QtCore.QPointF(x, y) for x, y in plist]
        self.polyg = QtGui.QPolygonF(self.pointList)
        self.newPos = QtCore.QPointF()
        self.lineColor = QtCore.Qt.black
        self.fillColor = QtCore.Qt.yellow
        self.geocode = geocode
        self.name = name
        self.setToolTip(str(self.geocode)+ " - "+name)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        # TODO: make item selectable (the above line is not working)
        self.setZValue(1)
    
    def type(self):
        return Polygon.Type
        
    def shape(self):
        path = QtGui.QPainterPath()
        #path.addRectF(self.xmin, self.ymin,self.width, self.height)
        path.addPolygon(self.polyg)
        return path

    def paint(self, painter, option, widget):
        painter.setBrush(self.fillColor)
        painter.setPen(QtGui.QPen(self.lineColor, 0))
        painter.drawPolygon(self.polyg)
        
    def mousePressEvent(self, event):
        button = event.button()
        print button
        scenepos = event.scenePos()
        pos = event.pos()
        if button ==2:
            pass
        if self.isSelected():
            print "unselect"
            self.setSelected(False)
            col = self.display.jet(self.display.timeseries[self.display.step][self.geocode])
            self.fillColor = QtGui.QColor(int(col[0]*255), int(col[1]*255), int(col[2]*255), int(col[3]*255))
        else: 
            print "select"
            self.setSelected(True)
            print self.isSelected()
            self.fillColor = QtCore.Qt.green
            self.display.addTsCurve(self.geocode, self.name)
            self.display.qwtPlot.replot()
        self.update()
        QtGui.QGraphicsItem.mousePressEvent(self, event)
        #TODO plotar a serie temporal neste evento

    def mouseReleaseEvent(self, event):
        self.update()
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)
        
    def mouseDoubleClickEvent(self, event):
        """
        Center the display on the coordinates of the double click
        """
        button = event.button()
        scenepos = event.scenePos()
        pos = event.pos()
        self.display.mapView.centerOn(scenepos)
    
    def boundingRect(self):
        return QtCore.QRectF(self.xmin, self.ymin,
                             self.width, self.height)
    

class QtGraph(BaseGraph):
    def __init__(self, display, **keywords):
        """
        Construct a Graph.  to be displayed with Python Visual
        """
        BaseGraph.__init__(self)
        self.display = display
        self.rect = None#xmin,ymin,xmax0,ymax
    
    def getRect(self):
        '''
        Returns the bounding rectangle for the graph
        '''
        if self.rect != None:
            for n in self.nodes:
                self.rect[0] = n.pos[0] if n.pos[0]<self.rect[0] else self.rect[0]
                self.rect[1] = n.pos[1] if n.pos[1]<self.rect[1] else self.rect[1]
                self.rect[2] = n.pos[0] if n.pos[0]>self.rect[2] else self.rect[2]
                self.rect[3] = n.pos[1] if n.pos[1]>self.rect[3] else self.rect[3]
        return self.rect

class QtNode(BaseNode,QtGui.QGraphicsItem):
    """
    Physical model and visual representation of a node as a mass using Qt
    """
    Type = QtGui.QGraphicsItem.UserType + 2
    def __init__(self, m, pos, r=1, display = None,  name='', **keywords):
        """
        Construct a mass.
        """
        BaseNode.__init__(self,  m, pos, r, **keywords)
        QtGui.QGraphicsItem.__init__(self)
        self.graph = display
        self.pos = pos
        self.r = r
        self.edgeList = []
        self.setZValue(3)
        #self.setPos(pos[0], pos[1])
        
    def type(self):
        return QtNode.Type
        
    def addEdge(self, edge):
        self.edgeList.append(edge)
        edge.adjust()

    def edges(self):
        return self.edgeList
        
    def boundingRect(self):
        return QtCore.QRectF(self.pos[0], self.pos[1],  self.r*2,  self.r*2)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.pos[0], self.pos[1], self.r*2,  self.r*2)
        return path

    def paint(self, painter, option, widget):
        painter.setBrush(QtCore.Qt.red)
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 0))
        painter.drawEllipse(self.pos[0], self.pos[1],  self.r*2,  self.r*2)

class QtRubberEdge(BaseRubberEdge):
    def __init__(self, n0, n1, k, l0=None, damping=None,
                 radius=None, color=(0.5,0.5,0.5), **keywords):
        """
        Construct a rubber spring.
        """
        BaseRubberEdge.__init__(self, n0, n1, k, l0, damping, radius, color, **keywords)

class MapServer:
    """
    xmlrpc server
    """
    def __init__(self, porta=50000):
        self.server = SimpleXMLRPCServer(("", porta))
        self.map = None
        self.step = 0
        self.jet  = cm.get_cmap("jet",50)
    
    def start(self):
        #self.server.register_function(self.map.drawStep)
        self.server.serve_forever()

        
if __name__=='__main__':
    app = QtGui.QApplication(sys.argv)
    QtCore.qsrand(QtCore.QTime(0,0,0).secsTo(QtCore.QTime.currentTime()))
    widget = MapWindow()
    widget.drawMap('riozonas_LatLong.shp','NOME_ZONAS','ZONA_TRAFE')
    widget.show()
    sys.exit(app.exec_())
    

##    n1 = Node(2,G.display.center)
##    n2 = Node(2,G.display.center+(1.,1.,1.))
##    n3 = Node(2,G.display.center+(1,2,3))
##    n4 = Node(2,G.display.center+(2,2,3))
##    G.insertNodeList([n1,n2,n3,n4])
##    e1 = RubberEdge(n1,n2,1, damping=.8)
##    e2 = RubberEdge(n2,n3,1, damping=.8)
##    e3 = RubberEdge(n2,n4,1, damping=.8)
##    e4 = RubberEdge(n4,n1,1, damping=.8)
##    G.insertEdgeList([e1,e2,e3,e4])
    

    #G.mainloop()
