#!/usr/bin/env python

#program to play simulations from database
import dgraph, cPickle, glob, os, ogr
import visual as V
import visual.graph as VG
from math import *
try:
    from PyQt4.QtGui import *
except ImportError: 
    print "Please install PyQT 4"
#from qt import *
from numpy import *
import sqlobject as SO
#from pylab import *
import pylab as P
from matplotlib.patches import Polygon
from matplotlib import cm


class viewer:
    """
    """
    def __init__(self, host='localhost', port=3306, user='epigrass', pw='epigrass', db='epigrass',backend='mysql',encoding='latin-1'):
        self.host = host
        self.port = port
        self.user = user
        self.pw = pw
        self.db = db
        self.backend = backend
        self.encoding = encoding
        
        if backend == 'sqlite':
            db_filename = os.path.abspath('Epigrass.db')
            connection_string = 'sqlite:' + db_filename
        elif backend == 'mysql':
            connection_string = r'%s://%s:%s@%s/%s'%(backend,user,pw,host,db)
        elif backend == 'csv':
            pass
        else:
            sys.exit('Invalid Database Backend specified: %s'%backend)
        if not backend == 'csv':
            self.connection = SO.connectionForURI(connection_string)
        
        self.dmap = 0#int(input('Draw Map?(0,1) '))
        self.tables = self.getTables()

        #self.nodes = self.readNodes(self.tables[table])
        #self.numbnodes = len(self.nodes)
        #self.data = self.readData(self.tables[table])
        #self.numbsteps = len(self.data)/self.numbnodes
        #self.viewGraph()
        
    def getTables(self):
        """
        Returns list of table names from current database connection
        """
        if self.backend == 'sqlite':
            r = [i[0] for i in self.connection.queryAll("select name from sqlite_master where type='table';")]
        elif self.backend == 'mysql':
            r = [i[0] for i in self.connection.queryAll('SHOW TABLES')]
        elif self.backend =='csv':
            r = glob.glob('*.tab')
        
        return r
    def getFields(self,table):
        """
        Returns a list of fields (column names) for a given table.
        table is a string with table name
        """
        if self.backend == 'sqlite':
            r = [i[1] for i in self.connection.queryAll('PRAGMA table_info(%s)'%table)]
        elif self.backend == 'mysql':
            r = [i[0] for i in self.connection.queryAll('SHOW FIELDS FROM %s'%table)]
        elif self.backend == 'csv':
            f = open(table,'r')
            r = f.read().strip().split(',')
            f.close()

        #select only the key names (each element in r is a tuple, containing
        # name and field descriptors )
        
        return r
    
    def readNodes(self,name,table):
        """
        Reads geocode and coords from database table
        for each node and adjacency matrix.
        """
        if self.backend =="csv":
            # the equivalent of a select for a csv file
            f=open(table,"r")
            names = f.readline().strip().split(",")#remove header
            d = {}
            for l in f:
                l=l.strip().split(',')
                d[l[names.index('geocode')]]=[l[names.index('geocode')],l[names.index('lat')],l[names.index('longit')],l[names.index('name')]]
            r= d.values()
            f.close()
                
        else:
            r = self.connection.queryAll('SELECT geocode,lat,longit,name FROM %s WHERE time = 0'%table)

        # get adjacency matrix
#        if not os.getcwd() == self.
        file = open('adj_'+name)
        m = cPickle.load(file)
        file.close()
        return r,m
    
    
    def readData(self,table):
        """
        read node time series data
        """
        if self.backend =="csv":
            f=open(table,"r")
            f.readline()#remove header
            r = []
            for l in f:
                l=l.strip().split(',')
                r.append(l)
            f.close()
        else:
            r = self.connection.queryAll('SELECT * FROM %s'%table)
        

        return r

    def readEdges(self,table):
        """
        Read edge time series
        """
        if self.backend =="csv":
            tab = table.split(".")[0]+"_e.tab"
            f = open(tab,"r")
            f.readline()#remove header
            r = [l.strip().split(',') for l in f]
            f.close()
        else:
            tab = table+'e'
            r = self.connection.queryAll('SELECT * FROM %s'%tab)

        return r
        
    def viewGraph(self, nodes, am, var,mapa=''):
        """
        Starts the Vpython display of the graph.
        """
        self.gr = dgraph.Graph(0.04, name='Epigrass Display - %s'%var)
        #self.gr.display.visible=0
        Nlist = [dgraph.Node(3,(float(i[2]),float(i[1]),0),name=unicode(i[3].strip(),self.encoding),geocode=i[0]) for i in nodes]
        self.gr.insertNodeList(Nlist)
        el = self.gr.getEdgeFromMatrix(am)
        #print am,el
        El = [dgraph.RubberEdge(self.gr.nodes[c],self.gr.nodes[l],1,damping=0.8) for c,l in el]
        #print El
        self.gr.insertEdgeList(El)
        self.gr.addTimelabel()
        self.gr.centerView()
        if mapa not in ['No map','Nenhum mapa','Pas de carte']:
            m = dgraph.Map(mapa,self.gr.display)
            self.gr.insertMap(m)
        else: m=None
        self.gr.centerView()
        if m:
            self.node_sizefactor = m.dimension/10000.
        else:
            self.node_sizefactor = self.gr.netdimension/10000.
        #self.gr.display.visible=1
            
    def anim(self,data,edata, numbsteps,pos, rate=20):
        """
        Starts the animation
        - data: time series from database
        - edata: infectious traveling for edge painting
        - pos: column number of variable to animate
        """
        for t in xrange(numbsteps):
            V.rate(rate)
            self.gr.timelabel.text=str(t) 
            for i,n in enumerate(self.gr.nodes):
                start = i*numbsteps+t
                try:
                    #print data[start][pos]
                    n.box.width = n.box.height = n.box.length = self.node_sizefactor *(log10(float(data[start][pos])+10))**1/3.
                    #print n.box.width
                except OverflowError:#handle the case of log(0)
                    n.box.width = n.box.height = n.box.length = 0.0001
                n.ts.append(float(data[start][pos]))
                if float(data[start][pos]) > 1:
                    self.paintNode(t,n,numbsteps)
                else:
                    self.paintNode(t,n,numbsteps,col='g')
            #paint Edges when there are infectious coming or going 
            if not edata:
                continue
            for i,e in enumerate(self.gr.edges):
                start = i*numbsteps+t
                if edata[start][-1]+edata[start][-2]:
                    e.cylinder.color = (255,0,0)#bright red
                else:
                    e.cylinder.color = (0.5,0.5,0.5)#dark gray
    
    def paintNode(self,t,node,numbsteps,col='r'):
        """
        Paints red the box corresponding to the node in the visual display
        """
        if col =='r':
            if not node.painted: 
                red = (int(numbsteps)-t)/float(numbsteps)
                blue = 1-red**6
                node.box.color = (red,0.,blue)
                node.painted = 1
        elif col =='g':
            node.box.color=V.color.green

    def plotTs(self,ts,name):
        """
        Uses gcurve to plot the time-series of a given city object
        """
##        try:
##            self.gg.display.visible=0
##        except:pass
        self.gg = VG.gdisplay(title='%s'%name,xtitle='time',ytitle='count')
        g=VG.gcurve(color=VG.color.green)
        for t,n in enumerate(ts):
            g.plot(pos=(t,n))
    
    def keyin(self,data,edata,numbsteps,pos,rate):
        """
        Implements keyboard and mouse interactions
        """
        while 1:
            ob = self.gr.display.mouse.pick
            try:
                ob.sn(2)
                if self.gr.display.mouse.alt and not ob.paren.tsdone:
                    self.plotTs(ob.paren.ts,ob.paren.name)
                    ob.paren.tsdone = 1
            except:pass
            if self.gr.display.mouse.clicked:
                m = self.gr.display.mouse.getclick()
                #print m.click
                loc = m.pos
                self.gr.display.center = loc
            if self.gr.display.kb.keys: # is there an event waiting to be processed?
                s = self.gr.display.kb.getkey() # obtain keyboard information
                if s == 'r': #Replay animation
                    for i in self.gr.nodes:
                        self.paintNode(0,i,numbsteps,col='g')
                        i.painted=0
                    self.anim(data,edata,numbsteps,pos,rate)
                else:
                    pass
    
    def viewGraph2D(self, fname, geocfield, canvas):
        """
        Starts the pylab display of the graph.
        fname: shapefile with the polygons
        """
        self.can = canvas

        ax = self.can.axes
        ax.set_title("Epidemic Dynamics")
        #Get the polygons
        g = ogr.Open (fname)
        L = g.GetLayer(0)
        N = 0
        pl = {}#polygon patch dictionary (by geocode)
        feat = L.GetNextFeature()
        while feat is not None:
            gc = feat.GetFieldAsInteger(geocfield)
            field_count = L.GetLayerDefn().GetFieldCount()
            geo = feat.GetGeometryRef()
            if geo.GetGeometryCount()<2:
                g1 = geo.GetGeometryRef( 0 )
                x =[g1.GetX(i) for i in xrange(g1.GetPointCount()) ]
                y =[g1.GetY(i) for i in xrange(g1.GetPointCount()) ]
                m=transpose(r_[[x],[y]]) #polygonvertices
                poligono = Polygon( m ,animated=True) #Define polygon
                #Add the polygon to the figure axes
                pl[gc]=poligono
                ax.add_patch ( poligono )
            for c in range( geo.GetGeometryCount()):
                ring = geo.GetGeometryRef ( c )
                for cnt in range( ring.GetGeometryCount()):
                    g1 = ring.GetGeometryRef( cnt )
                    x =[g1.GetX(i) for i in xrange(g1.GetPointCount()) ]
                    y =[g1.GetY(i) for i in xrange(g1.GetPointCount()) ]
                    m=transpose(r_[[x],[y]]) #Polygon vertices
                    poligono = Polygon( m ,animated=True) #Define polygon
                    #Add the polygon to the figure axes
                    pl[gc]=poligono
                    ax.add_patch ( poligono )
            feat = L.GetNextFeature()
        return ax, pl
            
    def anim2D(self,data,nodes, numbsteps,pos,ax,pl):
        """
        Starts the animation
        - data: time series from database
        - pos: column number of variable to animate
        - ax: is the axis containing the polygons
        - pl is the polygon dictionary
        """
        jet  = cm.get_cmap("jet",100)
        for t in range(numbsteps):
            for i in xrange(len(nodes)):
                start = i*numbsteps+t
                colmax = max([float(i[pos]) for i in data])
                colorind = float(data[start][pos])/colmax
                #print colorind
                color = jet(colorind)
                gc = int(data[start][0])
                try:
                    pl[gc].set_facecolor (color)
                except: pass
            self.can.draw()
    
if __name__ == "__main__":
    Display=viewer(user='root',pw='mysql')
    Display.anim()
    Display.keyin()
