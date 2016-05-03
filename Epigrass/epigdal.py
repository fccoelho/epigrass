"""
This module uses the GDAL and OGR Library to read maps in vaious formats and
export the results of Epigrass simulations to the formats supported by these libraries

copyright 2007,2012 by Flavio Codeco Coelho
Licensed under the GPL.
"""
import locale, os, pylab
from osgeo import ogr
from xml.dom import minidom, Node
from matplotlib.colors import rgb2hex, LogNorm
from matplotlib.colors import Normalize
from matplotlib import cm
from numpy import array
from zipfile import ZipFile
import json


class World:
    def __init__(self, filename, namefield, geocfield, outdir='.'):
        '''
        Instantiate a world object.
        Filename points to a file supported by OGR
        '''
        self.geocfield = geocfield
        self.namefield = namefield
        self.outdir = outdir
        self.ds = ogr.Open(filename)
        self.name = self.ds.GetName()
        self.driver = self.ds.GetDriver()
        self.centroids = []#centroid list (x,y,z) tuples
        self.centdict = {} #keys are geocode, values are (x,y,z) tuples
        self.geomdict = {} #keys are geocode, values are geometries
        self.namedict = {} #keys are geocode, values are locality names
        self.nlist = [] #nodelist: feature objects
        self.nodesource = False #True if Node datasource has been created
        self.edgesource = False #True if Edge datasource has been created
        self.datasource = False #True if Data datasource has been created
        self.layerlist = self.get_layer_list()

    def get_layer_list(self):
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

    def draw_layer(self, L):
        '''
        Draws a polygon layer using pylab
        '''
        N = 0
        L.ResetReading()
        feat = L.GetNextFeature()
        while feat is not None:
            field_count = L.GetLayerDefn().GetFieldCount()
            geo = feat.GetGeometryRef()
            if geo.GetGeometryCount() < 2:
                g1 = geo.GetGeometryRef(0)
                x = [g1.GetX(i) for i in range(g1.GetPointCount())]
                y = [g1.GetY(i) for i in range(g1.GetPointCount())]
                pylab.plot(x, y, '-', hold=True)
            for c in range(geo.GetGeometryCount()):
                ring = geo.GetGeometryRef(c)
                for cnt in range(ring.GetGeometryCount()):
                    g1 = ring.GetGeometryRef(cnt)
                    x = [g1.GetX(i) for i in range(g1.GetPointCount())]
                    y = [g1.GetY(i) for i in range(g1.GetPointCount())]
                    pylab.plot(x, y, '-', hold=True)
            feat = L.GetNextFeature()
        pylab.xlabel("Longitude")
        pylab.ylabel("Latitude")
        pylab.grid(True)
        pylab.show()

    def get_node_list(self, l):
        '''
        Updates self.centdict with centroid coordinates and self.nlist with layer features
        l is an OGR layer.
        '''
        self.nlist = []
        f = l.GetNextFeature()
        while f is not None:
            g = f.GetGeometryRef()
            self.geomdict[f.GetFieldAsInteger(self.geocfield)] = g
            try:
                c = g.Centroid()
                self.nlist.append(f)
                self.centdict[f.GetFieldAsInteger(self.geocfield)] = (c.GetX(), c.GetY(), c.GetZ())
                self.namedict[f.GetFieldAsInteger(self.geocfield)] = f.GetField(self.namefield)
            except: #in case feature is not a polygon
                print  f.GetFID(), g.GetGeometryType()
            f = l.GetNextFeature()
            #print (2600501 in self.centdict)


    def create_node_layer(self):
        """
        Creates a new shape file to represent network nodes.
        The node layer will be based on the centroids of the
        polygons belonging to the map layer associated with this
        world instance.
        namefield - name of the field containing polygon name
        geocfield - name of the field containing geocode
        """
        # Creates a new shape file to hold the data
        if os.path.exists(os.path.join(self.outdir, 'Nodes.shp')):
            os.remove(os.path.join(self.outdir, 'Nodes.shp'))
            os.remove(os.path.join(self.outdir, 'Nodes.shx'))
            os.remove(os.path.join(self.outdir, 'Nodes.dbf'))
        if not self.nodesource:
            dsn = self.driver.CreateDataSource(os.path.join(self.outdir, 'Nodes.shp'))
            self.nodesource = dsn
            nl = dsn.CreateLayer("nodes", geom_type=ogr.wkbPoint)
            #Create the fields
        fi1 = ogr.FieldDefn("name")
        fi2 = ogr.FieldDefn("geocode", field_type=ogr.OFTInteger)
        fi3 = ogr.FieldDefn("x", field_type=ogr.OFTString)
        fi4 = ogr.FieldDefn("y", field_type=ogr.OFTString)
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
            fe.SetField('name', f.GetField(self.namefield))
            fe.SetField('geocode', gc)
            fe.SetField('x', str(x))
            fe.SetField('y', str(y))
            pt = ogr.Geometry(type=ogr.wkbPoint)
            pt.AddPoint(x, y)
            fe.SetGeometryDirectly(pt)
            nl.CreateFeature(fe)
        nl.SyncToDisk()

    def create_edge_layer(self, elist):
        """
        Creates a new layer with edge information.
        elist is a list of tuples:
        (sgeoc,dgeoc,fsd,fds)
        """
        # Creates a new shape file to hold the data
        if os.path.exists(os.path.join(self.outdir, 'Edges.shp')):
            os.remove(os.path.join(self.outdir, 'Edges.shp'))
            os.remove(os.path.join(self.outdir, 'Edges.shx'))
            os.remove(os.path.join(self.outdir, 'Edges.dbf'))
        if not self.edgesource:
            dse = self.driver.CreateDataSource(os.path.join(self.outdir, 'Edges.shp'))
            self.edgesource = dse
            el = dse.CreateLayer("edges", geom_type=ogr.wkbLineString)
            #Create the fields
        fi1 = ogr.FieldDefn("s_geocode", field_type=ogr.OFTInteger)
        fi2 = ogr.FieldDefn("d_geocode", field_type=ogr.OFTInteger)
        fi3 = ogr.FieldDefn("flowSD", field_type=ogr.OFTReal)
        fi3.SetPrecision(12)
        fi4 = ogr.FieldDefn("flowDS", field_type=ogr.OFTReal)
        fi4.SetPrecision(12)
        el.CreateField(fi1)
        el.CreateField(fi2)
        el.CreateField(fi3)
        el.CreateField(fi4)
        #Add the features (lines)
        for e in elist:
            #print "setting edge fields"
            fe = ogr.Feature(el.GetLayerDefn())
            fe.SetField('s_geocode', e[0])
            fe.SetField('d_geocode', e[1])
            fe.SetField('flowSD', float(e[2]))
            fe.SetField('flowSD', float(e[3]))
            line = ogr.Geometry(type=ogr.wkbLineString)
            try:
                #print "creating edge lines"
                line.AddPoint(self.centdict[int(e[0])][0], self.centdict[int(e[0])][1])
                line.AddPoint(self.centdict[int(e[1])][0], self.centdict[int(e[1])][1])
                fe.SetGeometryDirectly(line)
                el.CreateFeature(fe)
            except: #node not in centdict
                pass
        el.SyncToDisk()

    def create_data_layer(self, varlist, data):
        """
        Creates a new shape to contain data about nodes.
        varlist is the list of fields names associated with
        the nodes.
        data is a list of lists whose first element is the geocode
        and the remaining elements are values of the fields, in the
        same order as they appear in varlist.
        """
        data = array(data)
        # building normalizers for each variable, except geocode
        norms = [Normalize(c.min(), c.max()) for c in data[:, 1:].T]
        if os.path.exists(os.path.join(self.outdir, 'Data.shp')):
            os.remove(os.path.join(self.outdir, 'Data.shp'))
            os.remove(os.path.join(self.outdir, 'Data.shx'))
            os.remove(os.path.join(self.outdir, 'Data.dbf'))
            # Creates a new shape file to hold the data
        if not self.datasource:
            dsd = self.driver.CreateDataSource(os.path.join(self.outdir, 'Data.shp'))
            self.datasource = dsd
            dl = dsd.CreateLayer("sim_results", geom_type=ogr.wkbPolygon)
            #Create the fields
        fi1 = ogr.FieldDefn("geocode", field_type=ogr.OFTInteger)
        fin = ogr.FieldDefn("name", field_type=ogr.OFTString)
        fic = ogr.FieldDefn("colors", field_type=ogr.OFTString)
        dl.CreateField(fi1)
        dl.CreateField(fin)
        dl.CreateField(fic) #json array with colors
        for v in varlist:
            #print "creating data fields"
            fi = ogr.FieldDefn(v, field_type=ogr.OFTReal)
            fi.SetPrecision(12)
            dl.CreateField(fi)

        #Add the features (points)
        for l in data:
        #            print l
            #Iterate over the lines of the data matrix.
            hexcolors = [self.get_hex_color(norms[i](v)) for i, v in enumerate(l[1:])]
            gc = l[0]
            try:
                geom = self.geomdict[gc]
            except KeyError: #Geocode not in polygon dictionary
                raise KeyError("Geocode %s not in polygon dictionary" % gc)
            if geom.GetGeometryType() != 3: continue
            #print geom.GetGeometryCount()
            fe = ogr.Feature(dl.GetLayerDefn())
            fe.SetField('geocode', gc)
            fe.SetField('name', self.namedict[gc])
            fe.SetField('colors', str(hexcolors))
            for v, d in zip(varlist, l[1:]):
                #print v,d
                fe.SetField(v, float(d))
                #Add the geometry
            #print "cloning geometry"
            clone = geom.Clone()
            #print geom
            #print "setting geometry"
            fe.SetGeometry(clone)
            #print "creating geom"
            dl.CreateFeature(fe)

        dl.SyncToDisk()
        self.save_data_geojson(dl)

    def get_hex_color(self, value):
        cols = cm.get_cmap("YlOrRd", 256)
        rgba = cols(value * 256)
        bgrcol = list(rgba[:-1]) #rgb(list)
        bgrcol.reverse() #turn it into bgr
        hexcol = "#80" + rgb2hex(bgrcol)[1:] #abgr Alpha set to 128
        return hexcol

    def save_data_geojson(self, dl, namefield=None):
        """
        Creates a GeoJSON file containin the polygon layer and results of the simulation
        :Parameters:
        :parameter dl: datalayer to save
        """
        print "==> saving to GeoJSON"
        spatial_reference = dl.GetSpatialRef()

        feature_collection = {"type": "FeatureCollection",
                              "features": []
        }

        #        if spatial_reference is not None:
        #            with open("data.crs", "wb") as f:
        #                f.write(spatial_reference.ExportToProj4())
        #
        #        feature_collection["crs"] = {"type": "link",
        #                                     "properties": {
        #                                         "href": "data.crs",
        #                                         "type": "proj4"
        #                                     }
        #        }
        if namefield is None:
            namefield = self.namefield
        dl.ResetReading()
        fe = dl.GetNextFeature()
        #        print fe
        while fe is not None:
        #            print namefield
            fi = fe.GetField('name')
            #            print fi,type(fi)
            try:
                fi = fi.decode('utf8', 'ignore')
            except AttributeError:
                fi = '' #name is None
            fe.SetField('name', str(fi))
            feature = json.loads(fe.ExportToJson())
            feature['properties']['colors'] = eval(feature['properties']['colors'])
            feature_collection["features"].append(feature)
            fe = dl.GetNextFeature()

        with open(os.path.join(self.outdir, 'data.json'), 'w') as f:
            json.dump(feature_collection, f)


    def gen_sites_file(self, fname):
        """
        This method generate a sites
        csv file from the nodes extracted from the
        map.
        """
        with open(fname, "w") as f:
            for fe in self.nlist:
                gc = fe.GetFieldAsInteger(self.geocfield)
                x = self.centdict[gc][0]
                y = self.centdict[gc][1]
                name = fe.GetField(self.namefield)
                line = "%s,%s,%s,%s\n" % (x, y, name, gc)
                #fe.SetField('name',f.GetField(self.namefield))
                f.write(line)


    def close_sources(self):
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


class AnimatedKML(object):
    """
    Creates animated KML based on layer given
    """

    def __init__(self, kmlfile, extrude=1):
        """
        kmlfile: File containing the layer over which the animation will be built. it must contain polygons. Placemarks should contain a tag <name> geocode</name>
        extrude: if True the polygons will be extruded according to values in the timeseries data.
        """
        self.extrude = extrude
        self.fname = kmlfile
        self.kmlDoc = minidom.parse(kmlfile)
        self.doc = self.kmlDoc.getElementsByTagName("Document")[0]
        ufElems = self.kmlDoc.getElementsByTagName("Placemark")
        self.pmdict = {}
        for e in ufElems:
            nel = e.getElementsByTagName("name")[0]
            name = self._get_text(nel.childNodes).split('-')[0]
            self.pmdict[name] = e

    def _get_text(self, nodelist):
        """
        Returns  the text of a xml text node
        """
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def add_data(self, data):
        """
        Add time-series data for the localities: [(geocode,time,value),...]
        """
        vals = array([i[2] for i in data])
        norm = Normalize(vals.min(), vals.max())
        for i, d in enumerate(data):
        #            print i, " of ",  len(data)
            pm = self.pmdict[d[0]]
            #clone placemark to receive new data
            pm_newtime = pm.cloneNode(1)
            # Renaming placemark
            on = pm_newtime.getElementsByTagName('name')[0]
            nn = self.kmlDoc.createElement('name')
            nn.appendChild(self.kmlDoc.createTextNode(d[0] + '-' + str(d[1])))
            pm_newtime.replaceChild(nn, on)
            nl = pm_newtime.childNodes
            #extrude polygon
            pol = pm_newtime.getElementsByTagName('Polygon')[0]
            alt = self.kmlDoc.createElement('altitudeMode')
            alt.appendChild(self.kmlDoc.createTextNode('relativeToGround'))
            ex = self.kmlDoc.createElement('extrude')
            ex.appendChild(self.kmlDoc.createTextNode('1'))
            ts = self.kmlDoc.createElement('tessellate')
            ts.appendChild(self.kmlDoc.createTextNode('1'))
            pol.appendChild(alt)
            pol.appendChild(ex)
            pol.appendChild(ts)
            lr = pm_newtime.getElementsByTagName('LinearRing')[0]
            nlr = self.extrude_polygon(lr, d[2])
            ob = pm_newtime.getElementsByTagName('outerBoundaryIs')[0]
            #            ob.replaceChild(nlr, lr)
            ob.removeChild(lr)
            ob.appendChild(nlr)
            #set polygon style
            col = rgb2hex(cm.jet(norm(d[2]))[:3]) + 'ff'
            st = pm_newtime.getElementsByTagName('Style')[0] #style
            nst = self.set_polygon_style(st, col)
            pm_newtime.removeChild(st)
            pm_newtime.appendChild(nst)

            #add timestamp
            ts = self.kmlDoc.createElement('TimeStamp')
            w = self.kmlDoc.createElement('when')
            w.appendChild(self.kmlDoc.createTextNode(str(d[1])))
            ts.appendChild(w)
            pm_newtime.appendChild(ts)
            self.doc.appendChild(pm_newtime)
        for pm in self.pmdict.itervalues():
            self.doc.removeChild(pm)
        self.pmdict = {}

    def extrude_polygon(self, lr, alt):
        """
        Adds altitude to the coordinates of the linear ring.
        """
        c = lr.getElementsByTagName('coordinates')[0]
        nc = self.kmlDoc.createElement('coordinates')
        ctext = self._get_text(c.childNodes)
        nctext = ' '.join([p + ',' + str(alt * 100) for p in ctext.split(' ')])
        nc.appendChild(self.kmlDoc.createTextNode(nctext))
        alt = self.kmlDoc.createElement('altitudeMode')
        alt.appendChild(self.kmlDoc.createTextNode('relativeToGround'))
        #        altoff = self.kmlDoc.createElement('altitudeOffset')
        #        altoff.appendChild(self.kmlDoc.createTextNode(str(d[2]*1000)))
        ex = self.kmlDoc.createElement('extrude')
        ex.appendChild(self.kmlDoc.createTextNode('1'))
        ts = self.kmlDoc.createElement('tessellate')
        ts.appendChild(self.kmlDoc.createTextNode('1'))
        lr.replaceChild(nc, c)
        lr.appendChild(alt)
        if self.extrude:
            lr.appendChild(ex)
            lr.appendChild(ts)
        #        lr.appendChild(altoff)
        return lr


    def set_polygon_style(self, style, color):
        st = style
        pst = st.getElementsByTagName('PolyStyle')[0] #polygon style
        pst1 = self.kmlDoc.createElement('PolyStyle')
        pfill = self.kmlDoc.createElement('fill')
        pcol = self.kmlDoc.createElement('color')
        pfill.appendChild(self.kmlDoc.createTextNode('1'))
        pcol.appendChild(self.kmlDoc.createTextNode(color))
        pst1.appendChild(pfill)
        pst1.appendChild(pcol)
        st.replaceChild(pst1, pst)
        return st

    def save(self, fname=''):
        """
        saves the new document
        """
        dir = os.path.split(self.fname)[0]

        if not fname:
            fname = self.fname.split('.')[0] + '_animation'
        else:
            fname = os.path.join(dir, fname)
        #        ld = zlib.compress(self.kmlDoc.toxml('utf-8'))
        with open(fname + '.kml', 'w') as f:
            f.write(self.kmlDoc.toprettyxml(indent='  ', encoding='utf-8'))
            # Now zip the kml to generate the kmz
        with ZipFile(fname + '.kmz', 'w', allowZip64=True) as kmz:
            kmz.write(fname + '.kml')
        os.unlink(fname + '.kml')


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
        kml.setAttribute("xmlns", "http://earth.google.com/kml/2.1")
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

    def get_hex_color(self, value):
        jet = cm.get_cmap("jet", 50)
        rgba = jet(value * 50)
        bgrcol = list(rgba[:-1]) #rgb(list)
        bgrcol.reverse() #turn it into bgr
        hexcol = "#80" + rgb2hex(bgrcol)[1:] #abgr Alpha set to 128
        return hexcol

    def addNodes(self, layer, names=None):
        """
        Adds a node to the document.
        d is the document element KML dom object.
        layer is a layer with polygons
        names is a dictionary of names indexed by geocode(int)
        """
        doc = self.dnode

        layer.ResetReading()
        while 1:
            f = layer.GetNextFeature()
            if not f:#exit after the last feature
                break
            prevalence = float(f.GetField("prevalence"))
            hexcol = self.get_hex_color(prevalence)
            g = f.GetGeometryRef()
            if g.GetGeometryType() == 3:
                geoc = f.GetFieldAsInteger("geocode")
                if not names:
                    name = ""
                else:
                    try:
                        name = str(geoc) + "-" + names[geoc]
                    except KeyError:
                        print geoc
                        name = ""
                description = "Prevalence: %s;\nTotal cases: %s;\nImported Cases: %s;" % (
                    prevalence, f.GetField("totalcases"), f.GetField("arrivals"))
                locale.setlocale(locale.LC_ALL, "C") #avoids conversion of decimal points
                gml = g.ExportToGML() #extract the coordinates from the GML representation
                coords = gml.split('<gml:coordinates>')[1].split('</gml:coordinates>')[0]
                coords = " ".join([i + ",0" for i in coords.split(" ")]) #add z coordinate
                #create the kml elements
                #placemark and sub elements
                pm = self.kmldoc.createElement("Placemark")
                nm = self.kmldoc.createElement("name")
                nm.appendChild(self.kmldoc.createTextNode(name))
                desc = self.kmldoc.createElement("description")
                desc.appendChild(self.kmldoc.createTextNode(description))
                pm.appendChild(nm)
                pm.appendChild(desc)
                #style and subelements
                st = self.kmldoc.createElement("Style")
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

    def writeToFile(self, dir):
        """
        Writes the kml file to disk
        """
        fullpath = os.path.join(dir, "Data.kml")
        f = open(fullpath, "w")
        f.write(self.kmldoc.toxml())
        f.close()


if __name__ == "__main__":
    # opening data source
    w = World('riozonas_LatLong.shp', 'nome_zonas', 'zona_trafe')
    layer = w.ds.GetLayerByName(w.layerlist[0])
    w.get_node_list(layer)
    w.draw_layer(layer)
    w.save_data_geojson(layer)
    w.create_node_layer()
    w.nodesource.Destroy() #flush data to disk
##    k = KmlGenerator()
##    k.addNodes(w.datasource.GetLayer(0))
##    k.writeToFile()
