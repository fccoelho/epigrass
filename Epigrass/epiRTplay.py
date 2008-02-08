#!/usr/bin/env python

#program to animate simulations in Real Time using Pyglet
import cPickle, glob, os, epigdal
from math import *
from pyglet import font
from pyglet import clock
from pyglet import window
from pyglet import image
from pyglet.gl import *
from pyglet.window import mouse
from pyglet.window import event
from pyglet.window import key
from numpy import *
from matplotlib import cm
from matplotlib.colors import rgb2hex
import primitives
import gdal,locale, ogr

class Viewer:
    """
    Pyglet OpenGL cotext to display epidemic dynamics
    """
    def __init__(self,graph, shpfname, geocfield, var="incidence"):
        self .graph  = graph
        self.var = var
        if graph:
            self.nodes = dict([(n.geocode, n) for n in graph.site_list])
        self.win = window.Window(visible=False)
        self.win.set_caption('Model Dynamics')
        self.polygons = self.drawMap(shpfname, geocfield)
        self.colmap  = cm.get_cmap("jet",100)
        
    def Show(self, timestep):
        """
        Shows the window and runs an update cycle.
        """
        if not self.win.visible:
            self.win.set_visible(True)
        self.win.dispatch_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for pol in self.polygons.items():
            color = self.colmap(self.nodes[pol[0]].__getattribute__(self.var)[timestep])
            pol[1].color = color
            pol[1].render()
            
        
        self.win.flip()
 

        
    def drawMap(self, fname, geocfield):
        """
        Draws the polygons of the model
        fname: shapefile with the polygons
        """
    
        #Get the polygons
        g = ogr.Open (fname)
        L = g.GetLayer(0)
        N = 0
        pl = {}#polygon patch dictionary (by geocode)
        feat = L.GetNextFeature()
        while feat is not None:
            try:
                gc = feat.GetFieldAsInteger(geocfield)
            except:
                gc = 0
            field_count = L.GetLayerDefn().GetFieldCount()
            geo = feat.GetGeometryRef()
            if geo.GetGeometryCount()<2:
                g1 = geo.GetGeometryRef( 0 )
                x =[g1.GetX(i) for i in xrange(g1.GetPointCount()) ]
                y =[g1.GetY(i) for i in xrange(g1.GetPointCount()) ]
                polv=zip(x, y) #Vertices do poligono
                poligono = primitives.Polygon(polv) #Definimos o poligono
                pl[gc]=poligono
            for c in range( geo.GetGeometryCount()):
                ring = geo.GetGeometryRef ( c )
                for cnt in range( ring.GetGeometryCount()):
                    g1 = ring.GetGeometryRef( cnt )
                    x =[g1.GetX(i) for i in range(g1.GetPointCount()) ]
                    y =[g1.GetY(i) for i in range(g1.GetPointCount()) ]
                    polv=zip(x, y) #Vertices do poligono
                    poligono = primitives.Polygon(polv, color=(.3,0.2,0.5,.7)) #Definimos o poligono
                    pl[gc]=poligono
                    
            feat = L.GetNextFeature()
        return pl
            
    def animReplay(self,var):
        """
        replays the animation for the given graph
        - data: time series from database
        - pos: column number of variable to animate
        - ax: is the axis containing the polygons
        - pl is the polygon dictionary
        """
        for step in xrange(0, self.graph.maxstep):
            self.show(step)
        
if __name__ == "__main__":
    Display=Viewer(None,'riozonas_LatLong.shp', 'geocode' )
    Display.win.set_visible(True)
    while not Display.win.has_exit:
        Display.win.dispatch_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        [pol[1].render() for pol in Display.polygons.items()]
        print "show"
        Display.win.flip()
    
