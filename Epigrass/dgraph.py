# ! /usr/bin/env python
"""
This module is a graph and map visualizing tool.

"""
import math
from osgeo import ogr
import threading
import itertools
import time, os, sys
from PyQt4 import Qt, QtCore, QtGui, QtOpenGL, Qwt5 as Qwt
from numpy import array, sqrt, average
from numpy.random import randint, uniform
from Ui_display import Ui_Form
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
    # if factor < 0.07 or factor > 1000000:
    #            return
    self.scale(scaleFactor, scaleFactor)


def timerEvent(self, event):
    pass

    for node in self.nodes:
        node.calculateForces()

    itemsMoved = False
    for node in self.nodes:
        if node.advance():
            itemsMoved = True

    if not itemsMoved:
        self.killTimer(self.timerId)
        self.timerId = 0


def itemMoved(self):
    if not self.timerId:
        self.timerId = self.startTimer(1000 / 25)


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


def array_dot(a, b):
    return sum([a[i] * b[i] for i in xrange(len(a))])


class MapWindow(QtGui.QWidget, Ui_Form):
    '''
    Map and Time-series window
    '''

    def __init__(self, G=None):
        QtGui.QWidget.__init__(self, None)
        self.Form = QtGui.QWidget()
        self.setupUi(self.Form)
        self.jet = cm.get_cmap("jet", 50)  # colormap
        self.timeseries = {}
        self.arrivals = {}
        self.colors = itertools.cycle(
            [Qt.Qt.red, Qt.Qt.green, Qt.Qt.blue, Qt.Qt.cyan, Qt.Qt.magenta, Qt.Qt.yellow, Qt.Qt.black, Qt.Qt.darkCyan,
             Qt.Qt.darkRed, Qt.Qt.darkGreen, Qt.Qt.darkBlue, Qt.Qt.darkMagenta, Qt.Qt.darkYellow])
        self.setupQwtPlot()
        self.step = 0
        self.M = None  # initialize map widget
        # Configuring View
        self.mapView.setViewportUpdateMode(QtGui.QGraphicsView.SmartViewportUpdate)

        # Overloading event-handling methods for self.mapView
        self.mapView.keyPressEvent = MethodType(keyPressEvent, self.mapView)
        self.mapView.wheelEvent = MethodType(wheelEvent, self.mapView)
        self.mapView.scaleView = MethodType(scaleView, self.mapView)
        # connections
        QtCore.QObject.connect(self.horizontalSlider, QtCore.SIGNAL("sliderReleased()"),
                               self.on_horizontalSlider_sliderMoved)
        QtCore.QObject.connect(self.horizontalSlider, QtCore.SIGNAL("valueChanged()"),
                               self.on_horizontalSlider_valueChanged)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL("released()"), self.replay)
        QtCore.QObject.connect(self.splitter, QtCore.SIGNAL("splitterMoved()"), self.centerScene)
        print hasattr(self, "showSumBox")
        QtCore.QObject.connect(self.showSumBox, QtCore.SIGNAL("stateChanged(int)"), self.on_showSumBox_stateChanged)

    #        self.server = MapServer()
    # self.server.map = self.M
    #        st = threading.Thread(target=self.server.start)
    #        st.start()

    def setupQwtPlot(self):
        """
        Sets up the time series plot
        """
        #        self.qwtPlot.setTitle('%s'%self.variable)
        self.qwtPlot.setAxisTitle(Qwt.QwtPlot.xBottom, 'time')
        #        self.qwtPlot.setAxisTitle(Qwt.QwtPlot.yLeft,  'count')
        self.qwtPlot.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.RightLegend)
        # Time marker
        self.mX = Qwt.QwtPlotMarker()
        self.mX.setLabel(Qwt.QwtText('t = '))
        self.mX.setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignTop)
        self.mX.setLineStyle(Qwt.QwtPlotMarker.VLine)
        self.mX.setXValue(0)
        self.mX.attach(self.qwtPlot)
        self.qwtPlot.replot()

    def fill_nodel_list(self, pl):
        """
        creates check boxes on the node list group box
        pl is a list of polygons
        """
        lo = self.nodeListLayout
        pl.sort(key=lambda p: p.name)  # adding sites in alphabetical order
        for n in pl:
            cb = QtGui.QCheckBox(self.scrollArea)
            cb.setText(n.name)
            QtCore.QObject.connect(cb, QtCore.SIGNAL("stateChanged(int)"), n.select)
            cb.setToolTip(str(n.geocode))
            lo.addWidget(cb)
        #        self.nodeGroupBox.setLayout(lo)

    def add_global_ts_curve(self, scope="all"):
        """
        Plots a time series which is the sum of all(scope="all") or 
        selected timeseries (scope="set")
        """
        t = self.timeseries.keys()
        t.sort()
        data = [0] * len(self.timeseries)
        if scope == "all":
            name = "Total"
            for k, v in self.timeseries.iteritems():
                data[k] = sum(v.values())
                # print v
        elif scope == "Selected":
            name = "Sum of Selected"
            #TODO: fix this
        #        print data
        curve = Qwt.QwtPlotCurve(name)
        pen = Qt.QPen(Qt.Qt.gray)
        pen.setStyle(4)
        pen.setWidth(3)
        curve.setPen(pen)
        curve.attach(self.qwtPlot)
        curve.setData(t, data)
        self.globalCurve = curve
        self.qwtPlot.replot()

    def addTsCurve(self, gc, name):
        """
        Plots a time series curve to the plot window
        """

        data = [0] * len(self.timeseries)
        for k, v in self.timeseries.iteritems():
            data[k] = v[gc]
        t = self.timeseries.keys()
        t.sort()
        curve = Qwt.QwtPlotCurve(name)
        curve.setPen(Qt.QPen(self.colors.next()))
        curve.attach(self.qwtPlot)
        curve.setData(t, data)
        self.M.polyDict[gc].curve = curve


    def drawMap(self, filename, namefield, geocfield):
        """
        Draws the map stored in the shapefile fname.
        """
        #Setup the Map
        self.M = Map(fname=filename, display=self, namefield=namefield, geocfield=geocfield)
        # self.server.map = self.M
        xmin, ymin = self.M.xmin, self.M.ymin
        xmax, ymax = self.M.xmax, self.M.ymax
        xxs = (xmax - xmin) * 1.1  #percentage of extra space
        yxs = (ymax - ymin) * 1.1  #percentage of extra space

        #calculating center of scene
        xc = (xmax + xmin) / 2.
        yc = (ymax + ymin) / 2.
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
        self.fill_nodel_list(self.M.polyList)
        #self.scene.addText("%s,%s,%s,%s"%(xmin, xxs, ymin, yxs))
        #        self.polys = [item for item in self.mapView.scene.items() if isinstance(item, Polygon)]
        #self.mapView.addGraph(self.polys)
        self.mapView.setMinimumSize(300, 300)
        #self.mapView.setWindowTitle(self.tr("Network View"))
        scale_factor = self.mapView.width() / xxs
        self.mapView.scale(scale_factor, scale_factor)
        if self.showSumBox.isChecked():
            self.add_global_ts_curve("all")
            #print self.polys

    def drawGraph(self, nlist, elist=[]):
        """
        Draws a graph in the scene
        nlist: is a lis of nodes in the format(x,y,geocode,name)
        elist: is a list of edges described by tuples of indices to the first list.
        """
        self.label.setText('Network View')
        self.M = Graph(self)
        self.mapView.timerId = 0
        #Adding graph event handlers
        self.mapView.itemMoved = MethodType(itemMoved, self.mapView)
        self.mapView.timerEvent = MethodType(timerEvent, self.mapView)
        self.mapView.scene = QtGui.QGraphicsScene(self.mapView)
        npos = [(n[1], -n[2]) for n in nlist]
        xmin, ymin = array(npos).min(axis=0)
        xmax, ymax = array(npos).max(axis=0)
        for n in nlist:
            node = Node(self.M, n[0], n[3])
            node.setPos(*(n[1], -n[2]))
            node.size = max(xmax - xmin, ymax - ymin) / math.sqrt(len(nlist)) * 0.5
            self.mapView.scene.addItem(node)
            self.M.insertNode(node)
            #print node.x(), node.y(), n.center[0], n.center[1]
        self.mapView.nodes = self.M.nodes
        for e in elist:
            ed = Edge(self.M.nodes[int(e[0])], self.M.nodes[int(e[1])])
            ed.arrowSize = max(xmax - xmin, ymax - ymin) / math.sqrt(len(nlist)) * 0.2
            self.mapView.scene.addItem(ed)
            self.M.insertEdge(ed)
        self.xmax, self.xmin = xmax, xmin
        self.ymax, self.ymin = ymax, ymin
        self.centerScene()


    def centerScene(self):
        """
        Centers the scene and fits the specified rectangle to it
        """
        ymax, ymin = self.ymax, self.ymin
        xmax, xmin = self.xmax, self.xmin
        xxs = (xmax - xmin) * 1.1  # percentage of extra space
        yxs = (ymax - ymin) * 1.1  # percentage of extra space
        #calculating center of scene

        xc = (xmax + xmin) / 2.
        yc = (ymax + ymin) / 2.
        self.mapView.scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        self.mapView.scene.setSceneRect(xmin, ymin, xxs, yxs)
        #        print self.mapView.scene.width(), self.mapView.scene.height()
        self.mapView.fitInView(xmin, ymin, xxs, yxs)
        self.mapView.setScene(self.mapView.scene)
        self.mapView.updateSceneRect(self.mapView.scene.sceneRect())
        self.mapView.centerOn(xc, yc)
        scale_factor = self.mapView.width() / xxs
        self.mapView.scale(scale_factor, scale_factor)

        self.mapView.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.mapView.setRenderHint(QtGui.QPainter.Antialiasing)
        self.mapView.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.mapView.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)


    def paintPols(self, datadict):
        """
        Paint the polygons with the data from data dict
        datadict is a dictionary of the form {geocode:value,...}
        """
        if max(datadict.values()) > 1:
            normw = max(datadict.values())
        else:
            normw = 1.
        for gc, val in datadict.iteritems():
            try:
                val /= normw  #normalize values if necessary
            except TypeError as e:
                print gc, val, datadict[gc], e
            col = self.jet(val)  # rgba list
            gc = int(gc)
            #            print gc, type(gc)
            if self.M.polyDict.has_key(gc):
                self.M.polyDict[gc].fillColor = QtGui.QColor(int(col[0] * 255), int(col[1] * 255), int(col[2] * 255),
                                                             int(col[3] * 255))
                self.M.polyDict[gc].update()
            #            else:
                # print self.M.polyDict.values()

    def replay(self):
        """
        Replay the time series from beggining to end.
        """
        rw = ReplayWorker(self.timeseries, self.arrivals)

        def stop_replay():
            rw.quit()

        QtCore.QObject.connect(rw, QtCore.SIGNAL("drawStep"), self.drawStep)
        QtCore.QObject.connect(rw, QtCore.SIGNAL("flash"), self.flashBorders)
        QtCore.QObject.connect(self.pushButton_2, QtCore.SIGNAL("released()"), stop_replay)
        rw.render()

    def drawStep(self, step, datadict={}):
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

    def flashBorders(self, step, gclist=[]):
        """
        Flash the borders to bright green to signal events
        gclist: list of geocodes to be flashed
        """
        self.arrivals[step] = gclist
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
        self.mX.setLabel(Qwt.QwtText("t = %s" % self.step))
        self.qwtPlot.replot()

    #    @QtCore.pyqtSignature("int")
    def on_showSumBox_stateChanged(self, st):
        """
        Handles adding/remove global timeseries curve
        """
        if st:
            #            print "adding global series"
            self.add_global_ts_curve()
        else:
            #            print "removing global series"
            self.globalCurve.detach()
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


def Edge(*args, **kwargs):
    if graphic_backend == "visual":
        return VisualEdge(*args, **kwargs)
    elif graphic_backend == "qt":
        return QtEdge(*args, **kwargs)
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


rho = 23.8732414637845  # for backwardscompatibility


class BaseNode(QtGui.QGraphicsItem):
    Type = QtGui.QGraphicsItem.UserType + 1

    def __init__(self, graphWidget):
        QtGui.QGraphicsItem.__init__(self)
        self.graph = graphWidget
        self.edgeList = []
        self.newPos = QtCore.QPointF()
        #        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setZValue(1)
        self.neighbors = []

    def type(self):
        return Node.Type

    def addEdge(self, edge):
        self.edgeList.append(edge)
        edge.adjust()

    def edges(self):
        return self.edgeList

    def calculateForces(self):
        if not self.scene() or self.scene().mouseGrabberItem() is self:
            self.newPos = self.pos()
            return

        # Sum up all forces pushing this item away.
        xvel = 0.0
        yvel = 0.0

    #        for item in self.graph.nodes:
    # line = QtCore.QLineF(self.mapFromItem(item, 0, 0), QtCore.QPointF(0, 0))
    #            dx = line.dx()
    #            dy = line.dy()
    #            l = 2.0 * (dx * dx + dy * dy)
    #            if l > 0:
    #                xvel += (dx * 150.0) / l
    #                yvel += (dy * 150.0) / l
    #
    #        # Now subtract all forces pulling items together.
    #        weight = (len(self.edgeList) + 1) * 10.0
    #        for edge in self.edgeList:
    #            if edge.sourceNode() is self:
    #                pos = self.mapFromItem(edge.destNode(), 0, 0)
    #            else:
    #                pos = self.mapFromItem(edge.sourceNode(), 0, 0)
    #            xvel += pos.x() / weight
    #            yvel += pos.y() / weight
    #
    #        if QtCore.qAbs(xvel) < 0.1 and QtCore.qAbs(yvel) < 0.1:
    #            xvel = yvel = 0.0

    #        sceneRect = self.scene().sceneRect()
    #        self.newPos = self.pos() + QtCore.QPointF(xvel, yvel)
    # self.newPos.setX(min(max(self.newPos.x(), sceneRect.left() + 10), sceneRect.right() - 10))
    #        self.newPos.setY(min(max(self.newPos.y(), sceneRect.top() + 10), sceneRect.bottom() - 10))

    def advance(self):
        pass


#        if self.newPos == self.pos():
#            return False
#
#        self.setPos(self.newPos)
#        return True

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
        self.polyDict = {}
        self.dragObject = None
        self.click = None
        self.distance = None
        self.timelabel = None
        self.rememberFixed = None
        self.rememberColor = None

        self.display = BaseBox()

    def insertNode(self, node):
        """
        Insert node into the system.
\        """
        #needs to be a list because the node index in this list identify it within the graph.

        #FIXME: verify time overhead of this check
        if not node in self.nodes:
            self.nodes.append(node)
            self.polyDict[node.geocode] = node
            node.graph = self  #pass a reference of self to the node.

    def insertMap(self, map_):
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
            for l in xrange(c + 1):  #scans only the lower triangle
                if matrix[l, c]:
                    el.append((c, l))
        return el


    def centerView(self):
        pass

    def advance(self):
        """
        Perform one Iteration of the system by advancing one timestep.
        """
        microstep = self.timestep / self.oversample
        center = visual.vector(0, 0, 0)
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
                self.center = center / float(len(self.nodes))
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
    def __init__(self, fname, namefield='NOME_ZONAS', geocfield='ZONA_TRAFE'):
        self.namefield = namefield
        self.geocfield = geocfield
        self.centroids = []  #centroid list (x,y,z) tuples
        self.centdict = {}  # keys are geocode, values are (x,y,z) tuples
        self.geomdict = {}  # keys are geocode, values are geometries
        self.nlist = []  # nodelist: feature objects
        self.polyList = []  # Qpolygon list: Polygon objects
        self.polyDict = {}
        if os.path.exists(fname):
            self.Reader(fname)
        else:
            # Check if it exist in parent directory
            upfname = os.path.join('..', fname)
            if os.path.exists(upfname):
                self.Reader(upfname)
            else:
                QtGui.QMessageBox.information(None,
                                              self.trUtf8("Map not found"),
                                              self.trUtf8(
                                                  """Neither {} nor {} were found in {}""".format(fname, upfname,
                                                                                                  os.getcwd())),
                                              self.trUtf8("&OK"))


    def Reader(self, fname):
        """
        Reads shapefiles vector files.
        """
        g = ogr.Open(fname)
        L = g.GetLayer(0)
        N = 0
        tp = []
        feat = L.GetNextFeature()
        while feat is not None:
            field_count = L.GetLayerDefn().GetFieldCount()
            geo = feat.GetGeometryRef()
            if geo.GetGeometryCount() < 2:
                g1 = geo.GetGeometryRef(0)
                geocode = feat.GetFieldAsInteger(self.geocfield)
                name = feat.GetFieldAsString(self.namefield)
                self.geomdict[geocode] = g1
                if g1.GetGeometryType() == 3:  #If it is a polygon
                    cen = g1.Centroid()
                    self.nlist.append(feat)
                    self.centdict[geocode] = (cen.GetX(), cen.GetY(), cen.GetZ())
                x = [g1.GetX(i) for i in xrange(g1.GetPointCount())]
                y = [-g1.GetY(i) for i in xrange(g1.GetPointCount())]
                lp = zip(x, y)  # list of points
                tp += lp
                # print geocode
                self.dbound(lp, geocode, name)
            for c in xrange(geo.GetGeometryCount()):
                ring = geo.GetGeometryRef(c)
                for cnt in xrange(ring.GetGeometryCount()):
                    g1 = ring.GetGeometryRef(cnt)
                    if g1.GetGeometryType() == 3:  # If it is a polygon
                        geocode = feat.GetFieldAsInteger(self.geocfield)
                        name = feat.GetFieldAsString(self.namefield)
                        self.geomdict[geocode] = g1
                        cen = g1.Centroid()
                        self.nlist.append(feat)
                        self.centdict[geocode] = (cen.GetX(), cen.GetY(), cen.GetZ())
                    x = [g1.GetX(i) for i in xrange(g1.GetPointCount())]
                    y = [-g1.GetY(i) for i in xrange(g1.GetPointCount())]
                    lp = zip(x, y)  # list of points
                    tp += lp
                    #                    print geocode
                    self.dbound(lp, geocode, name)
            feat = L.GetNextFeature()

        g.Destroy()
        tp = array(tp)
        self.dimension = tp.max()
        center = average(tp, axis=0)
        self.center = center

    def dbound(self, *args):
        pass


class QtMap(BaseMap):
    def __init__(self, fname, display=None, namefield='NOME_ZONAS', geocfield='ZONA_TRAFE'):
        self.display = display
        self.xmin, self.ymin, self.xmax, self.ymax = 180, 90, -180, -90
        BaseMap.__init__(self, fname, namefield, geocfield)

    def dbound(self, pol, geocode=None, name=""):
        """
        Draws a polygon.
        """
        #FIXME: consertar algoritmo para funcionar com qualquer sistema de coordenadas
        p = Polygon(pol, geocode, name, self.display)
        self.xmin = p.xmin if p.xmin < self.xmin else self.xmin
        self.ymin = p.ymin if p.ymin < self.ymin else self.ymin
        self.xmax = p.xmax if p.xmax > self.xmax else self.xmax
        self.ymax = p.ymax if p.ymax > self.ymax else self.ymax
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

    def __init__(self, plist, geocode, name, graphWidget):
        QtGui.QGraphicsItem.__init__(self)
        self.display = graphWidget
        self.xmin, self.ymin = (array(plist)).min(axis=0)
        self.xmax, self.ymax = (array(plist)).max(axis=0)
        self.center = ((self.xmax + self.xmin) / 2., (self.ymax + self.ymin) / 2.)
        self.width = self.xmax - self.xmin
        self.height = self.ymax - self.ymin
        self.plist = plist
        self.pointList = [QtCore.QPointF(x, y) for x, y in plist]
        self.polyg = QtGui.QPolygonF(self.pointList)
        self.newPos = QtCore.QPointF()
        self.lineColor = QtCore.Qt.black
        self.fillColor = QtCore.Qt.yellow
        self.geocode = geocode
        self.name = name
        self.setToolTip(str(self.geocode) + " - " + name)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
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
        #        print button
        scenepos = event.scenePos()
        pos = event.pos()
        self.select()
        #QtGui.QGraphicsItem.mousePressEvent(self, event)

    def select(self):
        """
        Toggle selection of polygon
        """
        if self.isSelected():
            #            print "unselect"
            self.setSelected(False)
            col = self.display.jet(self.display.timeseries[self.display.step][self.geocode])
            self.fillColor = QtGui.QColor(int(col[0] * 255), int(col[1] * 255), int(col[2] * 255), int(col[3] * 255))
            self.lineColor = QtCore.Qt.black
            self.curve.detach()
            self.display.qwtPlot.replot()
        else:
            #            print "select"
            self.setSelected(True)
            #            print self.isSelected()
            self.fillColor = QtCore.Qt.green
            self.lineColor = QtCore.Qt.white
            self.display.addTsCurve(self.geocode, self.name)
            self.display.qwtPlot.replot()
        self.update()

    def mouseReleaseEvent(self, event):
        self.update()
        #QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

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
        self.nodes = []
        self.polyDict = {}  #dictionary of nodes by geocode
        self.rect = [0, 0, 0, 0]  # xmin,ymin,xmax,ymax

    def getRect(self):
        '''
        Returns the bounding rectangle for the graph
        '''
        for n in self.nodes:
            self.rect[0] = n.pos.x() if n.pos.x() < self.rect[0] else self.rect[0]
            self.rect[1] = n.pos.y() if n.pos.y() < self.rect[1] else self.rect[1]
            self.rect[2] = n.pos.x() if n.pos.x() > self.rect[2] else self.rect[2]
            self.rect[3] = n.pos.y() if n.pos.y() > self.rect[3] else self.rect[3]
        return self.rect


class QtNode(BaseNode):
    """
    Physical model and visual representation of a node as a mass using Qt
    """

    def __init__(self, graphw, geocode, name):
        """
        Construct a mass.
        """
        BaseNode.__init__(self, graphw)
        self.edgeList = []
        self.geocode = geocode
        self.name = name
        self.fillColor = QtGui.QColor(255, 255, 0)
        self.size = 20
        self.setToolTip(str(self.geocode) + " - " + name)
        self.selected = False  # using our own selection flag to avoid conflicts with other stuff
        #self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)


    def mousePressEvent(self, event):
        if self.selected:
            #print "unselect"
            self.selected = False
            if self.graph.display.timeseries:
                col = self.graph.display.jet(self.graph.display.timeseries[self.graph.display.step][self.geocode])
                self.fillColor = QtGui.QColor(int(col[0] * 255), int(col[1] * 255), int(col[2] * 255),
                                              int(col[3] * 255))
            else:
                self.fillColor = QtGui.QColor(255, 255, 0)
            self.lineColor = QtCore.Qt.black
            self.curve.detach()
            self.graph.display.qwtPlot.replot()
        else:
            #print "select"
            self.selected = True
            #            print self.isSelected()
            self.fillColor = QtGui.QColor(0, 255, 0)
            self.lineColor = QtCore.Qt.white
            self.graph.display.addTsCurve(self.geocode, self.name)
            self.graph.display.qwtPlot.replot()
        self.update()

    #        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.update()
        #QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

    def type(self):
        return QtNode.Type

    def addEdge(self, edge):
        self.edgeList.append(edge)
        edge.adjust()

    def edges(self):
        return self.edgeList

    def boundingRect(self):
        adjust = 2.0
        return QtCore.QRectF(-10 - adjust, -10 - adjust,
                             23 + adjust, 23 + adjust)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(-10, -10, self.size, self.size)
        return path

    def paint(self, painter, option, widget):
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.darkGray)
        painter.drawEllipse(-7, -7, self.size, self.size)

        gradient = QtGui.QRadialGradient(-3, -3, 10)
        if option.state & QtGui.QStyle.State_Sunken:
            gradient.setCenter(3, 3)
            gradient.setFocalPoint(3, 3)
            gradient.setColorAt(1, QtGui.QColor(self.fillColor).light(120))
            gradient.setColorAt(0, QtGui.QColor(self.fillColor.darker(150)).light(120))
        else:
            gradient.setColorAt(0, self.fillColor)
            gradient.setColorAt(1, self.fillColor.darker(150))

        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 0))
        painter.drawEllipse(-10, -10, self.size, self.size)

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            pass
        #            for edge in self.edgeList:
        # edge.adjust()
        #self.graph.display.mapView.itemMoved()

        return QtGui.QGraphicsItem.itemChange(self, change, value)


class QtEdge(QtGui.QGraphicsItem):
    Pi = math.pi
    TwoPi = 2.0 * Pi
    Type = QtGui.QGraphicsItem.UserType + 2

    def __init__(self, sourceNode, destNode):
        QtGui.QGraphicsItem.__init__(self)
        self.arrowSize = 10.0
        self.sourcePoint = QtCore.QPointF()
        self.destPoint = QtCore.QPointF()
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self.source = sourceNode
        self.dest = destNode
        self.source.addEdge(self)
        self.source.neighbors.append(self.dest)
        self.dest.addEdge(self)
        self.dest.neighbors.append(self.source)
        self.adjust()

    def type(self):
        return QtEdge.Type

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

        line = QtCore.QLineF(self.mapFromItem(self.source, 0, 0), self.mapFromItem(self.dest, 0, 0))
        length = line.length()

        if length == 0.0:
            return

        edgeOffset = QtCore.QPointF((line.dx() * 10) / length, (line.dy() * 10) / length)

        self.prepareGeometryChange()
        self.sourcePoint = line.p1() + edgeOffset
        self.destPoint = line.p2() - edgeOffset

    def boundingRect(self):
        if not self.source or not self.dest:
            return QtCore.QRectF()

        penWidth = 1
        extra = (penWidth + self.arrowSize) / 2.0

        return QtCore.QRectF(self.sourcePoint,
                             QtCore.QSizeF(self.destPoint.x() - self.sourcePoint.x(),
                                           self.destPoint.y() - self.sourcePoint.y())).normalized().adjusted(-extra,
                                                                                                             -extra,
                                                                                                             extra,
                                                                                                             extra)

    def paint(self, painter, option, widget):
        if not self.source or not self.dest:
            return

        # Draw the line itself.
        line = QtCore.QLineF(self.sourcePoint, self.destPoint)

        if line.length() == 0.0:
            return

        painter.setPen(QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawLine(line)

        # Draw the arrows if there's enough room.
        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = QtEdge.TwoPi - angle

        sourceArrowP1 = self.sourcePoint + QtCore.QPointF(math.sin(angle + QtEdge.Pi / 3) * self.arrowSize,
                                                          math.cos(angle + QtEdge.Pi / 3) * self.arrowSize)
        sourceArrowP2 = self.sourcePoint + QtCore.QPointF(math.sin(angle + QtEdge.Pi - QtEdge.Pi / 3) * self.arrowSize,
                                                          math.cos(angle + QtEdge.Pi - QtEdge.Pi / 3) * self.arrowSize);
        destArrowP1 = self.destPoint + QtCore.QPointF(math.sin(angle - QtEdge.Pi / 3) * self.arrowSize,
                                                      math.cos(angle - QtEdge.Pi / 3) * self.arrowSize)
        destArrowP2 = self.destPoint + QtCore.QPointF(math.sin(angle - QtEdge.Pi + QtEdge.Pi / 3) * self.arrowSize,
                                                      math.cos(angle - QtEdge.Pi + QtEdge.Pi / 3) * self.arrowSize)

        painter.setBrush(QtCore.Qt.black)
        painter.drawPolygon(QtGui.QPolygonF([line.p1(), sourceArrowP1, sourceArrowP2]))
        painter.drawPolygon(QtGui.QPolygonF([line.p2(), destArrowP1, destArrowP2]))


class MapServer:
    """
    xmlrpc server
    """

    def __init__(self, porta=50000):
        self.server = SimpleXMLRPCServer(("", porta))
        self.map = None
        self.step = 0
        self.jet = cm.get_cmap("jet", 50)

    def start(self):
        #self.server.register_function(self.map.drawStep)
        self.server.serve_forever()


class ReplayWorker(QtCore.QThread):
    def __init__(self, ts, arr, period=.20, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.mutex = QtCore.QMutex()
        self.condition = QtCore.QWaitCondition()
        self.timeseries = ts
        self.arrivals = arr
        self.period = period

    def __del__(self):
        self.mutex.lock()
        self.condition.wakeOne()
        self.mutex.unlock()
        self.wait()

    def render(self):
        locker = QtCore.QMutexLocker(self.mutex)
        self.start()

    def run(self):
        for t in xrange(len(self.timeseries)):
            self.mutex.lock()
            self.emit(QtCore.SIGNAL("drawStep"), t, self.timeseries[t])
            self.mutex.unlock()
            if self.arrivals.has_key(t):
                self.emit(QtCore.SIGNAL("flash"), t, self.arrivals[t])
            #                self.flashBorders(t, self.arrivals[t])
            time.sleep(self.period)
        self.mutex.lock()
        self.condition.wait(self.mutex)
        self.mutex.unlock()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    QtCore.qsrand(QtCore.QTime(0, 0, 0).secsTo(QtCore.QTime.currentTime()))
    widget = MapWindow()
    widget.drawMap('riozonas_LatLong.shp', 'NOME_ZONAS', 'ZONA_TRAFE')
    # poslist = [(1, -50, -50, 'a'),(2, 0, -50, 'b'),(3, 50, -50, 'c'),(4, -50, 0,'d'),(5, 0, 0, 'e'),(6, 50, 0, 'f'),(7, -50, 50, 'g'),(8, 0, 50, 'h'),(9, 50, 50, 'i')]
    # elist = [(0,1),(1,2),(1,4),(2,5),(3,0),(3,4),(4,5),(4,7),(5,8),(6,3),(7,6),(8,7)]
    # widget.drawGraph(poslist, elist)
    widget.show()
    sys.exit(app.exec_())

