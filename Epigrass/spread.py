#
#spread display and analisys
#
try:
    from PyQt4.QtGui import *
except ImportError: 
    print "Please install PyQT 4"
#from qt import *
from xml.dom import minidom, Node
import dgraph, crypt, os, string
import visual as V
from math import *
from numpy import *
import codecs

class Spread:
    def __init__(self, graphobj, outdir='.',encoding='latin-1'):
        self.g = graphobj
        self.outdir = outdir
        self.encoding = encoding
        ct = self.cleanTree()
        #self.dotDraw(ct)
        self.writeGML(ct,outdir,encoding)
    
    def cleanTree(self):
        """
        Generates a unambiguous spread tree by selecting the most likely infector for each site
        """
        sptree=[]
        for i in self.g.epipath:
            #print i
            infectors = i[-1]
            # sorting infectors by number of infective contributed
            if len(infectors):
                reverse_infectors = [ [v[1],v[0]] for v in infectors.items()]
                reverse_infectors.sort()
                mli = [reverse_infectors[j][1] for j in range(0,len(reverse_infectors))][-1]#Most likely infector
            else:
                mli = 'NA'
            sptree.append((i[0],i[1].sitename,mli))
        return sptree
    
    def dotDraw(self,tr):
        """
        generate a jpeg image of the spread tree using pydot
        """
        edges = []
        for i in tr:
            edges.append((i[1],i[2]))
        dotg=pydot.graph_from_edges(edges)
        for e in tr: # label edges with date of infection
            dotg.get_edge(e[1],e[2]).label = str(e[0])
        dotg.write_raw('spreadtree.dot')
        #dotg.write_png('graph.jpg',prog='dot')
    
    
    def display(self):
        """
        display the epidemic tree
        """
        self.grd = dgraph.Graph(0.04, name= 'Epidemic Spread Display')
        #add time label
        V.label(pos=(0,20,3), text='Time', xoffset=0, yoffset=0, space=5, height=10, border=3, line=0)
        #add seed
        seed = dgraph.Node(2,(0,-10,0),r=5)
        seed.name = self.g.epipath[0][1].sitename
        nodes=[seed]
        edges=[]
        vpos = -10

        for n,i in enumerate(self.g.epipath):
            x= n*10
            y = vpos
            V.label(pos=(x,15,10), text=str(i[0]), xoffset=0, yoffset=0, space=5, height=10, border=3, line=1)
            nodes.append(dgraph.Node(2,(x,y,0),r=5))
            nodes[-1].name = i[1].sitename
            V.label(pos=(x,y,0), text=str(nodes[-1].name), xoffset=5, yoffset=5, space=0, height=10, border=3, line=1)
            nodes[-1].name = i[1].sitename
            vpos -= 10
            if i[2]:
                for j in i[2].keys():
                    #print j,i[2],nodes[-1].name
                    n2 = [k for k in nodes if crypt.crypt(k.name,'ab') == crypt.crypt(j,'ab')][0]
                    edges.append(dgraph.RubberEdge(nodes[-1],n2,1, damping=.8))
                    #edges[-1].cylinder.radius = log10(j[0])
        self.grd.insertNodeList(nodes)
        self.grd.insertEdgeList(edges)
        self.grd.centerView()


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
        print "Wrote %s"%fname
    writeGML = classmethod(writeGML)
        
    def writeENGML(self,fobj,tree):
        """
        Write the edges and Nodes section of a GML file
        """
        f=fobj
        #Create dictionary of node IDs, and eliminate possible node duplicates.
        nodes = dict([(i[1],n) for n,i in enumerate(tree)])
        for n,k in enumerate(nodes.iterkeys()):
            nodes[k] = n
        #writing nodes
        for i,n in nodes.iteritems():
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

class Consensus:
    def __init__(self,path,cutoff=0.0):
        tl = self.readTress(path)
        self.consensus(tl,cutoff)
    def readTress(self,path):
        """
        Read all files named epipath* from the current dir
        and return a collection of trees.
        """
        if not os.path.exists(path+'epipath.csv'):
            print "No tree files available on this path"
        else:
            f = open(path+'epipath.csv','r')
            treelist = [self.parseEpipath(f.readlines())]
            f.close()
            n=1
            fname = path+'epipath'+str(n)+'.csv'
            while os.path.exists(fname):
                f= open(fname, 'r')
                print "Reading %s ..." % fname
                treelist.append(self.parseEpipath(f.readlines()))
                f.close()
                n+=1
                fname = path+'epipath'+str(n)+'.csv'
        return treelist
        
        
    def parseEpipath(self,lines):
        """
        Receives a list of strings and returns a list of tuples
        """
        tree = [tuple(l[:-1].split(',')) for l in lines]
        return tree
        
    
    def consensus(self, treelist, cutoff):
        """
        Generate a consensus tree from the various trees generated by multiple runs.
        Saves the tree in gml format file
        """
        cons = {}
        trees = []
        for t in treelist:
            trees += t #concatenate all the trees
##        import tree 
##        cons = tree.tree(trees)
        #print len(trees)
        for i in trees[1:]:
            try:
                cons[i[1]+'-'+i[2]] += 1
            except:
                try:
                    cons[i[2]+'-'+i[1]] += 1
                except:
                    cons[i[1]+'-'+i[2]] = 1
        #print len(cons)
        
        maxsup = max(cons.values())
        const = [tuple([v]+k.split('-')) for k,v in cons.items()if float(v)/maxsup > cutoff[0]/100.]
        Spread.writeGML(const,'.','latin-1','consensus_tree.gml')
                 
