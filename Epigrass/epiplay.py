# !/usr/bin/env python

#program to play simulations from database
import dgraph, cPickle, glob, os, ogr, time
from math import *

try:
    from PyQt4.QtGui import *
except ImportError:
    print "Please install PyQT 4"
#
from numpy import *
from sqlsoup import SQLSoup as SqlSoup

from matplotlib import cm


class viewer:
    """
    """

    def __init__(self, host='localhost', port=3306, user='epigrass', pw='epigrass', db='epigrass', backend='mysql',
                 encoding='latin-1', gui=None):
        self.host = host
        self.port = port
        self.user = user
        self.pw = pw
        self.db = db
        self.backend = backend
        self.encoding = encoding
        self.gui = gui

        if backend == 'sqlite':
            db_filename = os.path.abspath('Epigrass.sqlite')
            connection_string = 'sqlite:///' + db_filename
        elif backend == 'mysql':
            connection_string = r'%s://%s:%s@%s/%s' % (backend, user, pw, host, db)
        elif backend == 'csv':
            pass
        else:
            sys.exit('Invalid Database Backend specified: %s' % backend)
        if not backend == 'csv':
            #self.connection = SO.connectionForURI(connection_string)
            self.connection = SqlSoup(connection_string)

        self.dmap = 0  # int(input('Draw Map?(0,1) '))
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
            r = self.connection.bind.table_names()
        #            r = [i[0] for i in self.connection.queryAll("select name from sqlite_master where type='table';")]
        elif self.backend == 'mysql':
            r = self.connection.bind.table_names()
        # r = [i[0] for i in self.connection.queryAll('SHOW TABLES')]
        elif self.backend == 'csv':
            r = glob.glob('*.tab')
        return r

    def getFields(self, table):
        """
        Returns a list of fields (column names) for a given table.
        table is a string with table name
        """
        if self.backend == 'sqlite':
            # r = [i[1] for i in self.connection.queryAll('PRAGMA table_info(%s)'%table)]
            #            shp =self.connection.queryAll('SELECT the_world$shapefile FROM %s'%(table+'_meta'))
            r = [i[1] for i in self.connection.bind.execute('PRAGMA table_info(%s)' % table).fetchall()]
            shp = self.connection.bind.execute('SELECT the_world$shapefile FROM %s' % (table + '_meta')).fetchall()
            self.shapefile = eval(shp[0][0])
            # print self.shapefile
        elif self.backend == 'mysql':
            #            r = [i[0] for i in self.connection.queryAll('SHOW FIELDS FROM %s'%table)]
            # shp =self.connection.queryAll('SELECT the_world$shapefile FROM %s'%(table+'_meta'))
            r = [i[0] for i in self.connection.bind.execute('SHOW FIELDS FROM %s' % table).fetchall()]
            shp = self.connection.bind.execute('SELECT the_world$shapefile FROM %s' % (table + '_meta')).fetchall()
            self.shapefile = eval(shp[0][0])
        elif self.backend == 'csv':
            with open(table, 'r') as f:
                r = f.read().strip().split(',')

        return r

    def readNodes(self, name, table):
        """
        Reads geocode and coords from database table
        for each node and adjacency matrix.
        """
        if self.backend == "csv":
            # the equivalent of a select for a csv file
            f = open(table, "r")
            names = f.readline().strip().split(",")  # remove header
            d = {}
            for l in f:
                l = l.strip().split(',')
                d[l[names.index('geocode')]] = [l[names.index('geocode')], l[names.index('lat')],
                                                l[names.index('longit')], l[names.index('name')]]
            r = d.values()
            f.close()
            self.numbnodes = len(r)
        else:
            #            r = self.connection.queryAll('SELECT geocode,lat,longit,name FROM %s WHERE time = 0'%table)
            r = self.connection.bind.execute('SELECT geocode,lat,longit,name FROM %s WHERE time = 0' % table).fetchall()
            self.numbnodes = len(r)
        self.nodes_pos = r  #[(i[1], i[2], i[0], i[3])for i in r]
        self.nodes_gc = [i[0] for i in r]

        # get adjacency matrix
        #        if not os.getcwd() == self.
        file = open('adj_' + name)
        m = cPickle.load(file)
        self.adjacency = m
        file.close()
        return r, m


    def readData(self, table):
        """
        Read node time series data
        """
        if self.backend == "csv":
            f = open(table, "r")
            f.readline()  #remove header
            r = []
            for l in f:
                l = l.strip().split(',')
                r.append(l)
            f.close()
        else:
            #            r = self.connection.queryAll('SELECT * FROM %s'%table)
            r = self.connection.bind.execute('SELECT * FROM %s' % table).fetchall()
        return r

    def readEdges(self, table):
        """
        Read edge time series
        """
        if self.backend == "csv":
            tab = table.split(".")[0] + "_e.tab"
            f = open(tab, "r")
            f.readline()  # remove header
            r = [l.strip().split(',') for l in f]
            f.close()
            self.numbedges = len(r)
        else:
            tab = table + 'e'
            # r = self.connection.queryAll('SELECT * FROM %s'%tab)
            r = self.connection.bind.execute('SELECT * FROM %s' % tab).fetchall()
            self.numbedges = len(r)
        self.elist = [(self.nodes_gc.index(e[0]), self.nodes_gc.index(e[1])) for e in r]
        if not self.elist:
            self.elist = transpose(self.adjacency.nonzero()).tolist()
        return r

    def viewGraph(self, nodes, am, var, mapa=''):
        """
        Starts the Qt display of the map or graph.
        """
        if self.shapefile:
            self.gui.openGraphDisplay(mapa, self.shapefile[1], self.shapefile[2], self.nodes_pos, self.elist)
        else:
            self.gui.openGraphDisplay(mapa, nlist=self.nodes_pos, elist=self.elist)
        self.gr = self.gui.graphDisplay
        self.gr.qwtPlot.setTitle(var)


    def anim(self, data, edata, numbsteps, pos, rate=20):
        """
        Starts the animation.
        * data: time series from database
        * edata: infectious traveling for edge painting
        * pos: column number of variable to animate
        """
        #FIXME: the animation rate is not working....
        self.gr.horizontalSlider.setEnabled(0)
        self.gr.horizontalSlider.setMaximum(numbsteps)
        for t in xrange(numbsteps):
            stepdict = {}
            for i in xrange(self.numbnodes):
                start = i * numbsteps + t
                stepdict[data[start][0]] = data[start][pos]  # {geocode: value}
            self.gr.drawStep(t, stepdict)
            #paint Edges when there are infectious coming or going 
            if not edata:
                continue
            elist = []
            for i in xrange(self.numbedges):
                start = i * numbsteps + t
                if edata[start][-1] + edata[start][-2]:
                    elist.append(edata[start][1])
            self.gr.flashBorders(elist)
        #            time.sleep(1./rate)
        self.gr.horizontalSlider.setEnabled(1)

#
#    def plotTs(self,ts,name):
#        """
#        Uses gcurve to plot the time-series of a given city object
#        """
###        try:
###            self.gg.display.visible=0
###        except:pass
#        self.gg = VG.gdisplay(title='%s'%name,xtitle='time',ytitle='count')
#        g=VG.gcurve(color=VG.color.green)
#        for t,n in enumerate(ts):
#            g.plot(pos=(t,n))

#    def keyin(self,data,edata,numbsteps,pos,rate):
#        """
#        Implements keyboard and mouse interactions
#        """
#        while 1:
#            ob = self.gr.display.mouse.pick
#            try:
#                ob.sn(2)
#                if self.gr.display.mouse.alt and not ob.paren.tsdone:
#                    self.plotTs(ob.paren.ts,ob.paren.name)
#                    ob.paren.tsdone = 1
#            except:pass
#            if self.gr.display.mouse.clicked:
#                m = self.gr.display.mouse.getclick()
#                #print m.click
#                loc = m.pos
#                self.gr.display.center = loc
#            if self.gr.display.kb.keys: # is there an event waiting to be processed?
#                s = self.gr.display.kb.getkey() # obtain keyboard information
#                if s == 'r': #Replay animation
#                    for i in self.gr.nodes:
#                        self.paintNode(0,i,numbsteps,col='g')
#                        i.painted=0
#                    self.anim(data,edata,numbsteps,pos,rate)
#                else:
#                    pass


if __name__ == "__main__":
    Display = viewer(user='root', pw='mysql')
    Display.anim()
    Display.keyin()
