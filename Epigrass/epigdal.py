"""
This module uses the GDAL and OGR Library to read maps in vaious formats and
export the results of Epigrass simulations to the formats supported by these libraries

copyright 2007 by Flavio Codeco Coelho
Licensed under the GPL.
"""
import locale, os#, pylab
from osgeo  import ogr,  gdal
from xml.dom import minidom, Node
from matplotlib.colors import  rgb2hex, LogNorm
from matplotlib import cm
class World:
    def __init__(self,filename,namefield='name',geocfield='geocode',outdir = '.'):
        '''
        Instantiate a world object.
        Filename points to a file supported by OGR
        '''
        self.geocfield = geocfield
        self.namefield = namefield
        self.outdir = outdir
        self.ds =ogr.Open(filename)
        self.name = self.ds.GetName()
        self.driver = self.ds.GetDriver()
        self.centroids = []#centroid list (x,y,z) tuples
        self.centdict = {} #keys are geocode, values are (x,y,z) tuples
        self.geomdict = {} #keys are geocode, values are geometries
        self.nlist = [] #nodelist: feature objects
        self.nodesource = False #True if Node datasource has been created
        self.edgesource = False #True if Edge datasource has been created
        self.datasource = False #True if Data datasource has been created
        self.layerlist = self.getLayerList()
    def getLayerList(self):
        """
        returns a list with the
        available layers by name
        """
        nlay = self.ds.GetLayerCount()
        ln = []
        for i in xrange(nlay):
            l = self.ds.GetLayer(i)
            ln.append(l.GetName())
        return ln

    def drawLayer(self,L):
        '''
        Draws a polygon layer using pylab
        '''
        N = 0
        L.ResetReading()
        feat = L.GetNextFeature()
        while feat is not None:
            field_count = L.GetLayerDefn().GetFieldCount()
            geo = feat.GetGeometryRef()
            if geo.GetGeometryCount()<2:
                g1 = geo.GetGeometryRef( 0 )
                x =[g1.GetX(i) for i in range(g1.GetPointCount()) ]
                y =[g1.GetY(i) for i in range(g1.GetPointCount()) ]
                pylab.plot(x,y,'-',hold=True)
            for c in range( geo.GetGeometryCount()):
                        ring = geo.GetGeometryRef ( c )
                        for cnt in range( ring.GetGeometryCount()):
                            g1 = ring.GetGeometryRef( cnt )
                            x =[g1.GetX(i) for i in range(g1.GetPointCount()) ]
                            y =[g1.GetY(i) for i in range(g1.GetPointCount()) ]
                            pylab.plot(x,y,'-',hold=True)
            feat = L.GetNextFeature()
        pylab.xlabel("Longitude")
        pylab.ylabel("Latitude")
        pylab.grid(True)
        pylab.show()

    def getNodeList(self,l):
        '''
        Returns the centroid coordinates
        l is an OGR layer.
        '''
        self.nlist=[]
        f = l.GetNextFeature()
        while f is not None:
            g = f.GetGeometryRef()
            self.geomdict[f.GetFieldAsInteger(self.geocfield)] = g
            try:
                c = g.Centroid()
                self.nlist.append(f)
                self.centdict[f.GetFieldAsInteger(self.geocfield)] = (c.GetX(),c.GetY(),c.GetZ())
            except: #in case feature is not a polygon
                print  f.GetFID(),g.GetGeometryType()
            f = l.GetNextFeature()
        #print (2600501 in self.centdict)


    def createNodeLayer(self):
        """
        Creates a new shape file to represent network nodes.
        The node layer will be based on the centroids of the
        polygons belonging to the map layer associated with this
        world instance.
        namefield - name of the field containing polygon name
        geocfield - name of the field containing geocode
        """
        # Creates a new shape file to hold the data
        if os.path.exists(os.path.join(self.outdir,'Nodes.shp')):
            os.remove(os.path.join(self.outdir,'Nodes.shp'))
            os.remove(os.path.join(self.outdir,'Nodes.shx'))
            os.remove(os.path.join(self.outdir,'Nodes.dbf'))
        if not self.nodesource:
            dsn = self.driver.CreateDataSource(os.path.join(self.outdir,'Nodes.shp'))
            self.nodesource = dsn
            nl = dsn.CreateLayer("nodes",geom_type=ogr.wkbPoint)
        #Create the fields
        fi1 = ogr.FieldDefn("name")
        fi2 = ogr.FieldDefn("geocode",field_type=ogr.OFTInteger)
        fi3 = ogr.FieldDefn("x",field_type=ogr.OFTString)
        fi4 = ogr.FieldDefn("y",field_type=ogr.OFTString)
        nl.CreateField(fi1)
        nl.CreateField(fi2)
        nl.CreateField(fi3)
        nl.CreateField(fi4)
        #Add the features (points)
        for f in self.nlist:
            gc = f.GetFieldAsInteger(self.geocfield)
            x = self.centdict[gc][0]
            y = self.centdict[gc][1]
            fe = ogr.Feature(nl.GetLayerDefn())
            name = f.GetField(self.namefield)
            fe.SetField('name',f.GetField(self.namefield))
            fe.SetField('geocode',gc)
            fe.SetField('x',str(x))
            fe.SetField('y',str(y))
            pt = ogr.Geometry(type=ogr.wkbPoint)
            pt.AddPoint(x,y)
            fe.SetGeometryDirectly(pt)
            nl.CreateFeature(fe)
        nl.SyncToDisk()

    def createEdgeLayer(self,elist):
        """
        Creates a new layer with edge information.
        elist is a list of tuples:
        (sgeoc,dgeoc,fsd,fds)
        """
        # Creates a new shape file to hold the data
        if os.path.exists(os.path.join(self.outdir,'Edges.shp')):
            os.remove(os.path.join(self.outdir,'Edges.shp'))
            os.remove(os.path.join(self.outdir,'Edges.shx'))
            os.remove(os.path.join(self.outdir,'Edges.dbf'))
        if not self.edgesource:
            dse = self.driver.CreateDataSource(os.path.join(self.outdir,'Edges.shp'))
            self.edgesource = dse
            el = dse.CreateLayer("edges",geom_type=ogr.wkbLineString)
        #Create the fields
        fi1 = ogr.FieldDefn("source_geocode",field_type=ogr.OFTInteger)
        fi2 = ogr.FieldDefn("dest_geocode",field_type=ogr.OFTInteger)
        fi3 = ogr.FieldDefn("flowSD",field_type=ogr.OFTReal)
        fi3.SetPrecision(12)
        fi4 = ogr.FieldDefn("flowDS",field_type=ogr.OFTReal)
        fi4.SetPrecision(12)
        el.CreateField(fi1)
        el.CreateField(fi2)
        el.CreateField(fi3)
        el.CreateField(fi4)
        #Add the features (lines)
        for e in elist:
            #print "setting edge fields"
            fe = ogr.Feature(el.GetLayerDefn())
            fe.SetField('source_geocode',e[0])
            fe.SetField('dest_geocode',e[1])
            fe.SetField('flowSD',e[2])
            fe.SetField('flowSD',e[3])
            line = ogr.Geometry(type=ogr.wkbLineString)
            try:
                #print "creating edge lines"
                line.AddPoint(self.centdict[int(e[0])][0],self.centdict[int(e[0])][1])
                line.AddPoint(self.centdict[int(e[1])][0],self.centdict[int(e[1])][1])
                fe.SetGeometryDirectly(line)
                el.CreateFeature(fe)
            except: #node not in centdict
                pass
        el.SyncToDisk()

    def createDataLayer(self,varlist, data):
        """
        Creates a new shape to contain data about nodes.
        varlist is the list of fields names associated with
        the nodes.
        data is a list of lists whose first element is the geocode
        and the remaining elements are values of the fields, in the
        same order as they appear in varlist.
        """
        if os.path.exists(os.path.join(self.outdir,'Data.shp')):
            os.remove(os.path.join(self.outdir,'Data.shp'))
            os.remove(os.path.join(self.outdir,'Data.shx'))
            os.remove(os.path.join(self.outdir,'Data.dbf'))
        # Creates a new shape file to hold the data
        if not self.datasource:
            dsd = self.driver.CreateDataSource(os.path.join(self.outdir,'Data.shp'))
            self.datasource = dsd
            dl = dsd.CreateLayer("sim_results",geom_type=ogr.wkbPolygon)
        #Create the fields
        fi1 = ogr.FieldDefn("geocode",field_type=ogr.OFTInteger)
        dl.CreateField(fi1)
        for v in varlist:
            #print "creating data fields"
            fi = ogr.FieldDefn(v,field_type=ogr.OFTString)
            fi.SetPrecision(12)
            dl.CreateField(fi)

        #Add the features (points)
        for n,l in enumerate(data):
            #Iterate over the lines of the data matrix.
            gc = l[0]
            try:
                geom = self.geomdict[gc]
                if geom.GetGeometryType() != 3: continue
                #print geom.GetGeometryCount()
                fe = ogr.Feature(dl.GetLayerDefn())
                fe.SetField('geocode',gc)
                for v,d in zip (varlist,l[1:]):
                    #print v,d
                    fe.SetField(v,str(d))
                #Add the geometry
                #print "cloning geometry"
                clone = geom.Clone()
                #print geom
                #print "setting geometry"
                fe.SetGeometry(clone)
                #print "creating geom"
                dl.CreateFeature(fe)
            except: #Geocode not in polygon dictionary
                pass
            dl.SyncToDisk()

    def genSitesFile(self,fname):
        """
        This method generate a sites
        csv file from the nodes extracted from the
        map.
        """
        f = open(fname,"w")
        for fe in self.nlist:
            gc = fe.GetFieldAsInteger(self.geocfield)
            x = self.centdict[gc][0]
            y = self.centdict[gc][1]
            name = fe.GetField(self.namefield)
            line = "%s,%s,%s,%s\n"%(x,y,name,gc)
            #fe.SetField('name',f.GetField(self.namefield))
            f.write(line)
        f.close()


    def closeSources(self):
        """
        Close the data sources so that data is flushed and and files are closed
        """
        if self.nodesource:
            self.nodesource.Destroy()
            #print "closed node files"
        if self.edgesource:
            self.edgesource.Destroy()
            #print "closed edge files"
        if self.datasource:
            self.datasource.Destroy()
            #print "closed data files"


class KmlGenerator:
    """
        Generate a KML file for displaying data on 
        Google Maps/Earth
    """
    def __init__(self):
        self.doc = None
        self.dnode = None #document node in the DOM
        self.genRoot()
    def genRoot(self):
        """
        Generate a KML file root.
        """
        self.kmldoc = doc = minidom.Document()
        kml = doc.createElement("kml")
        kml.setAttribute("xmlns","http://earth.google.com/kml/2.1")
        doc.appendChild(kml)
        d = doc.createElement("Document")
        kml.appendChild(d)
        nel = doc.createElement("name")
        name = doc.createTextNode("KML Epigrass data file")
        nel.appendChild(name)
        d.appendChild(nel)
        desc = doc.createElement("description")
        d.appendChild(desc)
        desc.appendChild(doc.createTextNode("Polygons with data"))
        self.dnode = d

    def addNodes(self,layer,names=None):
        """
        Adds a node to the document.
        d is the document element KML dom object.
        layer is a layer with polygons
        names is a dictionary of names indexed by geocode(int)
        """
        doc = self.dnode
        jet  = cm.get_cmap("jet",50)
        layer.ResetReading()
        while 1:
            f = layer.GetNextFeature()
            if not f:#exit after the last feature
                break
            prevalence = float(f.GetField("prevalence"))
            rgba = jet(prevalence)
            bgrcol = list(rgba[:-1]) #rgb(list)
            bgrcol.reverse() #turn it into bgr
            hexcol = "#80"+rgb2hex(bgrcol)[1:] #abgr Alpha set to 128
            g = f.GetGeometryRef()
            if g.GetGeometryType() == 3:
                if not names:
                    name = ""
                else:
                    try:
                        name = names[f.GetFieldAsInteger("geocode")]
                    except KeyError:
                        print f.GetFieldAsInteger("geocode")
                        name = ""
                description = "Prevalence: %s;\nTotal cases: %s;\nImported Cases: %s;"%(prevalence,f.GetField("totalcases"),f.GetField("arrivals"))
                locale.setlocale(locale.LC_ALL,"C") #avoids conversion of decimal points
                gml = g.ExportToGML() #extract the coordinates from the GML representation
                coords = gml.split('<gml:coordinates>')[1].split('</gml:coordinates>')[0]
                coords  = " ".join([i+",0" for i in coords.split(" ")]) #add z coordinate
                #create the kml elements
                #placemark and sub elements
                pm=self.kmldoc.createElement("Placemark")
                nm = self.kmldoc.createElement("name")
                nm.appendChild(self.kmldoc.createTextNode(name))
                desc = self.kmldoc.createElement("description")
                desc.appendChild(self.kmldoc.createTextNode(description))
                pm.appendChild(nm)
                pm.appendChild(desc)
                #style and subelements
                st=self.kmldoc.createElement("Style")
                pm.appendChild(st)
                ps = self.kmldoc.createElement("PolyStyle")
                color = self.kmldoc.createElement("color")
                color.appendChild(self.kmldoc.createTextNode(hexcol))
                ps.appendChild(color)
                fill = self.kmldoc.createElement("fill")
                fill.appendChild(self.kmldoc.createTextNode("1"))
                ps.appendChild(fill)
                outline = self.kmldoc.createElement("outline")
                outline.appendChild(self.kmldoc.createTextNode("1"))
                ps.appendChild(outline)
                st.appendChild(ps)
                doc.appendChild(pm)
                #Multigeometry
                mg = self.kmldoc.createElement("MultiGeometry")
                pm.appendChild(mg)
                polygon = self.kmldoc.createElement("Polygon")
                mg.appendChild(polygon)
                ob = self.kmldoc.createElement("outerBoundaryIs")
                polygon.appendChild(ob)
                linr = self.kmldoc.createElement("LinearRing")
                ob.appendChild(linr)
                coordin = self.kmldoc.createElement("coordinates")
                linr.appendChild(coordin)
                coordin.appendChild(self.kmldoc.createTextNode(coords))
    def writeToFile(self,dir):
        """
        Writes the kml file to disk
        """
        fullpath = os.path.join(dir,"Data.kml")
        f=open(fullpath,"w")
        f.write(self.kmldoc.toxml())
        f.close()

if __name__=="__main__":
    # opening data source
    w = World('riozonas_LatLong.shp','nome_zonas','zona_trafe')
    layer = w.ds.GetLayerByName(w.layerlist[0])
    w.getNodeList(layer)
    w.drawLayer(layer)
    w.createNodeLayer()
    w.nodesource.Destroy() #flush data to disk
##    k = KmlGenerator()
##    k.addNodes(w.datasource.GetLayer(0))
##    k.writeToFile()
