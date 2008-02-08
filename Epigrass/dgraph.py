"""
This module is a graph visualizing tool.
It tries to resolves the graph layout by making an analogy
of the nodes and edges to masses and springs.
the nodes repel each other with a force inversely proportional to their
distance, and the edges do the opposite.
"""
import math, ogr
from numpy import *
import visual, time, os
#from pylab import *
##import psyco
##psyco.full()

graphic_backend = "visual"

#FIXME: check numpy functions for vector arithmetics:

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
        #these proeperties  have to be defined in each subclass.
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


class VisualNode(BaseNode):
    """
    Physical model and visual representation of a node as a mass using Visual Python
    """
    def __init__(self, m, pos, r=.1, fixed=0, pickable=1, v=(0., 0., 0.), color=(0., 1., 0.), name='', **keywords):
        """
        Construct a mass.
        """
        BaseNode.__init__(self,  m, pos, r,
                          fixed, pickable, v,
                          color, name, **keywords)

        self.box = visual.box(pos=visual.vector(pos),
                              length=float(self.r),height=self.r,
                              width=self.r,color=color,
                              name='',**keywords)

        self.box.Name = visual.label(pos=visual.vector(pos),
                                     text=self.name, xoffset=20,
                                     yoffset=20, space=0, height=10,
                                     box=0, border=6, line=1,visible=0)

        self.box.sn = self.showName
        self.box.paren = self #the node instance owning this box.

    def showName(self,t):
        """
        Show the node name for t seconds
        """
        self.box.Name.visible=1
        time.sleep(t)
        self.box.Name.visible=0

    def calcNewLocation(self, dt):
        """
        Calculate the new location of the mass.
        """
        # F = m * a = m * dv / dt  =>  dv = F * dt / m
        dv = self.F * dt / self.m
        self.v += dv
        # v = dx / dt  =>  dx = v * dt
        self.pos += self.v * dt
        self.box.pos += visual.vector(self.v) * dt

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


class VisualRubberEdge(BaseRubberEdge):
    """
    Visual representation of a spring using a single cylinder with variable radius.
    """

    def __init__(self, n0, n1, k, l0=None, damping=None,
                 radius=None, color=(0.5,0.5,0.5), **keywords):
        """
        Construct a rubber spring.
        """
        BaseRubberEdge.__init__(self, n0, n1, k, l0, damping,
                                radius, color, **keywords)

        self.cylinder = visual.cylinder(pos=visual.vector(self.n0.pos),
                                        axis=visual.vector(self.n1.pos -
                                                           self.n0.pos),
                                        radius=self.r0, color=color,
                                        **keywords)

    def update(self):
        """
        Update the visual representation of the spring.
        """
        self.cylinder.pos = visual.vector(self.n0.pos)
        self.cylinder.axis = visual.vector(self.n1.pos - self.n0.pos)


class BaseGraph(object):
    """
    The Graph.self.data(start)[5]
    """
    def __init__(self, timestep, oversample=1, gravity=1, viscosity=None, name='EpiGrass Viewer', **keywords):
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

        #self.display = visual.display(title=name, ambient=0.5, **keywords)
        #self.display.select()


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
        for c in range(siz):
            for l in range(c+1): #scans only the lower triangle
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

class VisualGraph(BaseGraph):
    """
    The Graph.self.data(start)[5]
    """
    def __init__(self, timestep, oversample=1, gravity=1,
                 viscosity=None, name='EpiGrass Viewer',
               **keywords):
        """
        Construct a Graph.  to be displayed with Python Visual
        """
        BaseGraph.__init__(self,timestep, oversample, gravity,
                            viscosity, name, **keywords)

        self.display = visual.display(title=name, ambient=0.5, **keywords)
        self.display.select()


    def addTimelabel(self):
        """
        Adds the time label at the center of the display
        """
        self.timelabel = visual.label(pos=self.display.center,
                                      text='0', xoffset=0, yoffset=0,
                                      space=5, height=10, border=6, line=0)

    def centerView(self):
        points = array([i.box.pos for i in self.nodes])
        self.netdimension = points.max()
        cnt = average(points,0)
        self.display.center = cnt
        if self.timelabel:
            self.timelabel.pos = cnt + visual.vector(0.,0.,2.)


    def advance(self):
        """
        Perform one Iteration of the system by advancing one timestep.
        """
        BaseGraph.advance(self)
        self.display.center = self.center

    def dispatchDnD(self):
        """Process the drag and drop interaction from the mouse.
        """
        if self.display.mouse.clicked:
            self.click = self.display.mouse.getclick()
            if self.dragObject: # drop the selected object
                # restore original attributes
                self.dragObject.node.fixed = self.rememberFixed
                self.dragObject.color = self.rememberColor
                # no initial velocity after dragging
                self.dragObject.node.v = visual.vector(0., 0., 0.)
                self.dragObject = None
            elif self.click.pick and self.click.pick.__class__ == 'sphere' and self.click.pick.node.pickable: # pick up the object (but only masses)
                self.dragObject = self.click.pick
                self.distance = visual.dot(self.display.forward, self.dragObject.pos)
                # save original attributes and overwrite them
                self.rememberFixed = self.dragObject.node.fixed
                self.dragObject.node.fixed = 1
                self.rememberColor = self.dragObject.color
                self.dragObject.color = (self.rememberColor[0] * 1.5,
                                         self.rememberColor[1] * 1.5,
                                         self.rememberColor[2] * 1.5)
        if self.dragObject:
            self.dragObject.pos = self.display.mouse.project(normal=self.display.forward, d=self.distance)

    def step(self):
        """Perform one step.  This is a convenience method.
        It actually calls dispatchDnD() and advance().
        """
        self.dispatchDnD()
        self.advance()
        visual.rate(self.rate) # best when placed after advance() and before dispatchDnD()

    def mainloop(self):
        """Start the mainloop, which means that step() is
        called in an infinite loop.
        """
        #self.display.autoscale=0
        while 1:
            self.step()

class BaseMap(object):
    def __init__(self, fname):
        if os.path.exists(fname):
            self.Reader(fname)
        else:
            print "shapefile not found"


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
                x =[g1.GetX(i) for i in range(g1.GetPointCount()) ]
                y =[g1.GetY(i) for i in range(g1.GetPointCount()) ]
                lp = zip(x,y)#list of points
                tp += lp
                self.dbound(lp)
            for c in range( geo.GetGeometryCount()):
                ring = geo.GetGeometryRef ( c )
                for cnt in range( ring.GetGeometryCount()):
                    g1 = ring.GetGeometryRef( cnt )
                    x =[g1.GetX(i) for i in range(g1.GetPointCount()) ]
                    y =[g1.GetY(i) for i in range(g1.GetPointCount()) ]
                    lp = zip(x,y)#list of points
                    tp += lp
                    self.dbound(lp)
            feat = L.GetNextFeature()

        g.Destroy()
        tp = array(tp)
        self.dimension = tp.max()
        center = average(tp,axis=0)
        self.center = center

    def dbound(self, *args):
        pass

class VisualMap(BaseMap):
    def __init__(self, fname, display=None):
        self.display = display
        BaseMap.__init__(self, fname)


    def Reader(self, fname):
        """
        Reads shapefiles vector files.
        """
        BaseMap.Reader(self, fname)
        self.display.center = self.center


    def dbound(self,pol):
        """
        Draws a polygon
        """
        visual.curve(pos=pol,radius = 0)

if __name__=='__main__':
    G = Graph(0.04)

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
    M = Map('riozonas_LatLong.shp',G.display)

    #G.mainloop()
