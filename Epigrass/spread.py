#coding: utf8
#spread display and analisys

from __future__ import absolute_import
from __future__ import print_function
from xml.dom import minidom, Node
import os, json
from numpy import *
import networkx as nx
from networkx.readwrite import  json_graph
import codecs
import six

class Spread:
    def __init__(self, graphobj, outdir='.',encoding='utf-8'):
        self.g = graphobj
        self.nxg = nx.MultiDiGraph()
        self.outdir = outdir
        self.encoding = encoding
        self.create_tree()
        nx.write_graphml(self.nxg,os.path.join(outdir,'spread.graphml'),encoding=encoding)
        nx.write_gml(self.nxg,os.path.join(outdir,'spread.gml'))
        nl = json_graph.node_link_data(self.nxg)
        with open(os.path.join(outdir,'spread.json'),'w') as f:
            json.dump(nl,f)
#        nx.write_dot(self.nxg,os.path.join(outdir,'spread.graphml'))
#        graphml = GraphML(self.g, outdir, encoding)
#        graphml.write()
    
    def create_tree(self):
        """
        Generates a unambiguous spread tree by selecting the most likely infector for each site
        """
        #Creating nodes and edges
        for n in self.g.epipath:
            infected = self.g.site_dict[n[1]]
            infectors = n[-1]
            self.nxg.add_node(n[1],name=infected.sitename,time=n[0])
            for  i, c in six.iteritems(infectors):
                self.nxg.add_edge(n[1],i.geocode,weight=float(c))


    def writeGML(self,tree, outdir,encoding,fname="spreadtree.gml"):
        """
        Save the tree in the GML format
        """
        try:
            os.chdir(outdir)
        except:
            pass
        dir(self)
        f = codecs.open(fname,'w', encoding)
        f.writelines(['Creator "Epigrass"\n',
        'Version ""\n',
        'graph\n[\n',
        '\thierarchic\t1\n'
        '\tlabel\t"Spread Tree"\n'
        '\tdirected\t1\n'])
        #self.writeENGML(f,tree)
        Spread.writeENGML(f,tree) #calling as a class method
        f.write(']')
        f.close()
        print("Wrote %s"%fname)
    writeGML = classmethod(writeGML)
        
    def writeENGML(self,fobj,tree):
        """
        Write the edges and Nodes section of a GML file
        """
        f=fobj
        #Create dictionary of node IDs, and eliminate possible node duplicates.
        nodes = dict([(i[1],n) for n,i in enumerate(tree)])
        for n,k in enumerate(six.iterkeys(nodes)):
            nodes[k] = n
        #writing nodes
        for i,n in six.iteritems(nodes):
            f.writelines(['\tnode\n','\t[\n'])
            f.writelines(['\t\tid\t%s\n'%n,'\t\tlabel\t"%s"\n'%i])
            f.writelines(['\t\tgraphics\n','\t\t[\n','\t\t\tw\t60\n','\t\t\th\t30\n'])
            f.writelines(['\t\t\ttype\t"roundrectangle"\n','\t\t\tfill\t"#FFCC00"\n','\t\t\toutline\t"#000000"\n','\t\t]\n'])
            f.writelines(['\t\tLabelGraphics\n','\t\t[\n','\t\t\ttext\t"%s"\n'%i,'\t\t\tfontSize\t13\n','\t\t\tfontName\t"Dialog"\n','\t\t\tanchor\t"c"\n','\t\t]\n','\t]\n'])
        #writing Edges
        for n,i in enumerate(tree):
            lab = str(i[0])
            tid = nodes[i[1]]
            try: #If the source is NA (seed site)
                sid = nodes[i[2]]
            except KeyError:
                continue
            #print lab
            f.writelines(['\tedge\n','\t[\n'])
            f.writelines(['\t\tsource\t%s\n'%sid,'\t\ttarget\t%s\n'%tid,'\t\tlabel\t"%s"\n'%lab,'\t\tgraphics\n','\t\t[\n'])
            f.writelines(['\t\t\tfill\t"#000000"\n','\t\t\ttargetArrow\t"standard"\n','\t\t]\n','\t]\n'])
    writeENGML = classmethod(writeENGML)

#class GraphML:
#    def __init__(self,graphobj,  outdir, encoding,fname="spread.graphml" ):
#        """
#        Generates a valid GraphML document from the spread tree.
#        """
#        self.g = graphobj
#        self.encoding = encoding
#        self.outdir = outdir
#        self.fname = fname
#        self.doc = minidom.Document()
#        # Creating Root element
#        gml = self.doc.createElement("graphml")
#        gml.setAttribute("xmlns","http://graphml.graphdrawing.org/xmlns")
#        gml.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
#        gml.setAttribute("xsi:schemaLocation", "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd")
#        self.addAttrKeys(gml)
#
#        # Creating graph Element
#        self.gr = self.doc.createElement("graph")
#        self.gr.setAttribute("id", "graphname")
#        self.gr.setAttribute("edgedefault", "directed")
#
#        #Creating nodes and edges
#        self.nodes = []
#        for n in self.g.epipath:
#            infected = self.g.site_dict[n[1]]
#            infectors = n[-1]
#            self.addNodeEl(n[1], infected.sitename)
#            self.nodes.append(n[1])
#            for  i, c in infectors.iteritems():
#                self.addNodeEl(i.geocode, i.sitename)
#                self.addEdgeEl(i.geocode, n[1], n[0], c)
#        gml.appendChild(self.gr)
#        self.doc.appendChild(gml)
#
#    def addNodeEl(self, gc , name):
#        """
#        Adds a Node element to the Graphml object
#        """
#        if gc in self.nodes:
#            return
#        else:
##            print gc, name
#            nd = self.doc.createElement("node")
#            nd.setAttribute("id", "n"+str(gc))
#            data = self.doc.createElement("data")
#            data.setAttribute("key", "d0")
#            data.appendChild(self.doc.createTextNode(name))
#            nd.appendChild(data)
#            self.gr.appendChild(nd)
#
#    def addEdgeEl(self, s, d , t, ino):
##        print s, d , t , ino
#        ed = self.doc.createElement("edge")
#        ed.setAttribute("source", str(s))
#        ed.setAttribute("target", str(d))
#        data = self.doc.createElement("data")
#        data.setAttribute("key", "d1")
#        data.appendChild(self.doc.createTextNode(str(ino)))
#        ed.appendChild(data)
#        data = self.doc.createElement("data")
#        data.setAttribute("key", "d2")
#        data.appendChild(self.doc.createTextNode(str(t)))
#        ed.appendChild(data)
#        self.gr.appendChild(ed)
#
#    def addAttrKeys(self, gml):
#        k1 = self.doc.createElement("key")
#        k1.setAttribute("id", "d0")
#        k1.setAttribute("for", "node")
#        k1.setAttribute("attr.name", "label")
#        k1.setAttribute("attr.type", "string")
#        gml.appendChild(k1)
#        k2 = self.doc.createElement("key")
#        k2.setAttribute("id", "d1")
#        k2.setAttribute("for", "edge")
#        k2.setAttribute("attr.name", "Innoculum")
#        k2.setAttribute("attr.type", "int")
#        gml.appendChild(k2)
#        k3 = self.doc.createElement("key")
#        k3.setAttribute("id", "d2")
#        k3.setAttribute("for", "edge")
#        k3.setAttribute("attr.name", "timestep")
#        k3.setAttribute("attr.type", "int")
#        gml.appendChild(k3)
#    def write(self):
#        """
#        Writes the graphml file to disk
#        """
#        fullpath = os.path.join(self.outdir,self.fname)
#        f=open(fullpath,"w")
##        f.write('<?xml version="1.0" encoding="%s"?>'%self.encoding)
#        f.write(self.doc.toprettyxml(encoding=self.encoding))
#        f.close()
#
#class Consensus:
#    def __init__(self,path,cutoff=0.0):
#        tl = self.readTress(path)
#        self.consensus(tl,cutoff)
#    def readTress(self,path):
#        """
#        Read all files named epipath* from the current dir
#        and return a collection of trees.
#        """
#        if not os.path.exists(path+'epipath.csv'):
#            print "No tree files available on this path"
#        else:
#            f = open(path+'epipath.csv','r')
#            treelist = [self.parseEpipath(f.readlines())]
#            f.close()
#            n=1
#            fname = path+'epipath'+str(n)+'.csv'
#            while os.path.exists(fname):
#                f= open(fname, 'r')
#                print "Reading %s ..." % fname
#                treelist.append(self.parseEpipath(f.readlines()))
#                f.close()
#                n+=1
#                fname = path+'epipath'+str(n)+'.csv'
#        return treelist
#
#
#    def parseEpipath(self,lines):
#        """
#        Receives a list of strings and returns a list of tuples
#        """
#        tree = [tuple(l[:-1].split(',')) for l in lines]
#        return tree
#
#
#    def consensus(self, treelist, cutoff):
#        """
#        Generate a consensus tree from the various trees generated by multiple runs.
#        Saves the tree in gml format file
#        """
#        cons = {}
#        trees = []
#        for t in treelist:
#            trees += t #concatenate all the trees
###        import tree
###        cons = tree.tree(trees)
#        #print len(trees)
#        for i in trees[1:]:
#            try:
#                cons[i[1]+'-'+i[2]] += 1
#            except:
#                try:
#                    cons[i[2]+'-'+i[1]] += 1
#                except:
#                    cons[i[1]+'-'+i[2]] = 1
#        #print len(cons)
#
#        maxsup = max(cons.values())
#        const = [tuple([v]+k.split('-')) for k,v in cons.items()if float(v)/maxsup > cutoff[0]/100.]
#        Spread.writeGML(const,'.','latin-1','consensus_tree.gml')
#
