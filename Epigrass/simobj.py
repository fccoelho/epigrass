"""
This Module contains the definitions of objects for spatial simulation on geo reference spaces.
"""
from __future__ import absolute_import
from __future__ import print_function
import sys
import multiprocessing
import time
import json
import os
import numpy as np
from numpy.random import binomial
import networkx as NX
from networkx.exception import NetworkXNoPath, NetworkXError
from networkx.readwrite import json_graph
import redis

from Epigrass.data_io import *
from Epigrass import models

try:
    sys.path.insert(0, os.getcwd())
    import CustomModel
except ImportError as exc:
    print("No Custom Model Available.")
    CustomModel = None

# Setup Redis database to making sharing of state between nodes efficient during parallel execution of the simulation
redisclient = redis.Redis(host='localhost', port=6379)
assert redisclient.ping()  # verify that redis server is running.

# logger = multiprocessing.log_to_stderr()
# logger.setLevel(multiprocessing.SUBDEBUG)
# logger.setLevel(logging.INFO)

sys.setrecursionlimit(3000)  # to allow pickling of custom models

PO = multiprocessing.Pool(multiprocessing.cpu_count())


class siteobj:
    """
    Basic site object containing attributes and methods common to all
    site objects.
    """

    def __init__(self, name, initpop, coords, geocode, values=()):
        """
        Set initial values for site attributes.

        -name: name of the locality

        -coords: site coordinates.

        -initpop: total population size.

        -geocode: integer id code for site

        -values: Tuple containing adicional values from the sites file
        """
        self.id = self  # reference to site instance
        self.stochtransp = 0  # Flag for stochastic transportation
        self.pos = coords
        self.totpop = float(initpop)
        self.ts = []
        self.incidence = []
        self.infected = False
        self.infector = None
        self.sitename = name
        self.values = values
        self.centrality = None
        self.betweeness = None
        self.thidx = None
        self.degree = None
        self.parentGraph = None
        self.edges = []
        self.neighbors = []
        self.thetalist = []
        self.thetahist = []  # infected arriving per time step
        self.passlist = []
        self.totalcases = 0
        self.vaccination = [[], []]  # time and coverage of vaccination event
        self.vaccineNow = 0  # flag to indicate that it is vaccination day
        self.vaccov = 0  # current vaccination coverage
        self.nVaccinated = 0
        self.quarantine = [sys.maxsize, 0]
        self.nQuarantined = 0
        self.geocode = geocode
        self.painted = 0  # Flag for the graph display
        self.modtype = None
        self.migInf = []  # infectious individuals able to migrate (time series)
        self.inedges = []  # Inbound edges
        self.outedges = []  # outbound edges
        self.pdest = []
        self.infectedvisiting = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        redisclient.set("{}:totalcases".format(self.geocode), 0)

    def __call__(self):
        """
        For multiprocessing to work
        """
        t0 = time.time()
        self.runModel()
        print("Time to runModel: ", time.time() - t0)
        return self

    def createModel(self, modtype='', name='model1', v=[], bi=None, bp=None):
        """
        Creates a model of type modtype and defines its initial parameters.
        init -- initial conditions for the state variables tuple with fractions of the total
        population in each category (state variable).
        par -- initial values for the parameters.
        v -- List of extra variables passed in the sites files
        bi, bp -- dictionaries containing all the inits and parms defined in the .epg model
        """
        # Init = init  # deprecated
        N = self.totpop
        self.modtype = bytes(modtype, 'utf8')
        self.values = v
        self.bi = bi
        self.bp = bp
        if modtype in ['Custom', 'custom']:
            if CustomModel is None:
                raise ImportError(
                    "You have to Create a CustomModel.py file before you can select\nthe Custom model type")
            self.model = CustomModel.Model
            self.vnames = CustomModel.vnames
        else:
            self.model = models.Epimodel(self.geocode, self.modtype)
            self.vnames = models.vnames[modtype]
        try:
            # self.ts = [[bi[vn.lower()] for vn in self.vnames]]
            self.ts.append(list(bi.values()))  # This is fine since bi is an OrderedDict
        except KeyError as ke:
            if self.vnames == ['Exposed', 'Infectious', 'Susceptible']:
                self.ts = [[bi[vn] for vn in ['e', 'i', 's']]]
            else:
                raise KeyError('%s' % ke)
        self.bp['vaccineNow'] = 0
        self.bp['vaccov'] = 0

    #        self.model = popmodels(self.id,type=modtype,v=self.values,bi = self.bi, bp = self.bp)

    def runModel(self, parallel=True):
        """
        Iterate the model
        :Parameters:
        - parallel: run in a separate process if true
        """

        if self.parentGraph.simstep in self.vaccination[0]:
            self.vaccineNow = 1
            self.vaccov = float(self.vaccination[1][self.vaccination[0].index(self.parentGraph.simstep)])
            self.bp['vaccineNow'] = 1
            self.bp['vaccov'] = self.vaccov
        else:
            self.bp['vaccineNow'] = 0
        if self.thetalist != []:
            theta = sum([i[1] for i in self.thetalist])
            self.infector = dict(
                [i for i in self.thetalist if i[1] > 0])  # Only those that contribute at least one infected individual
        else:
            theta = 0
            self.infector = {}
        npass = sum(self.passlist)
        simstep = self.parentGraph.simstep
        inits = self.ts[-1]
        totpop = self.totpop
        # print("writing inits: ", inits)
        # ---------------------
        # print ([type(x) for x in [totpop, npass, theta, simstep]] )
        pipe = redisclient.pipeline()
        pipe.set("simstep", simstep)
        pipe.set("{}:totpop".format(self.geocode), totpop)
        # pipe.rpush("{}:inits".format(self.geocode), str(inits))
        pipe.rpush("{}:ts".format(self.geocode), str(inits))
        pipe.set("{}:npass".format(self.geocode), float(npass))
        pipe.set("{}:theta".format(self.geocode), int(nan_to_num(theta)))
        pipe.hmset("{}:bi".format(self.geocode), self.bi)
        pipe.hmset("{}:bp".format(self.geocode), self.bp)
        pipe.execute()
        # ------------------------
        if parallel:
            # r = self.parentGraph.po.apply_async(self.model, args=(inits, simstep, totpop, theta, npass, self.bi,
            #                                                       self.bp, self.values), callback=self.handle)
            r = PO.apply_async(self.model, args=(), callback=self.handle)
        else:
            res = self.model(inits, simstep, totpop, theta, npass, self.bi, self.bp, self.values)
            self.handle(res)
            r = None

        self.thetahist.append(theta)  # keep a record of infected passenger arriving
        return r

    #        state, Lpos, migInf = self.model.step(inits=self.ts[-1],simstep=simstep,totpop=self.totpop,theta=theta,npass=npass)

    def handle(self, res):
        """
        Processes the output of a step updating simulation statistics
        :param res: Tuple with the output of the simulation model
        """
        last_state = eval(redisclient.lindex("{}:ts".format(self.geocode), -1))
        # try:
        #     assert res[0] == last_state
        # except:
        #     pass
        Lpos = redisclient.lindex(f"{self.geocode}:incidence", -1)
        migInf = redisclient.get("{}:migInf".format(self.geocode))
        self.ts.append(last_state)
        Lpos = float(Lpos)
        migInf = float(migInf)
        self.totalcases += Lpos
        self.incidence.append(Lpos)
        if not self.infected:
            if Lpos > 0:
                self.infected = self.parentGraph.simstep
                self.parentGraph.epipath.append((self.parentGraph.simstep, self.geocode, self.infector))
                # TODO: have infector be stated in terms of geocodes
        self.migInf.append(migInf)

    def vaccinate(self, cov):
        """
        At time t the population will be vaccinated with coverage cov.
        """
        self.nVaccinated = self.ts[-1][2] * cov
        self.ts[-1][2] = self.ts[-1][2] * (1 - cov)

    def intervention(self, par, cov, efic):
        """
        From time t on, parameter par is changed to
        par * (1-cov*efic)
        """
        self.bp[par] = self.bp[par] * (1 - cov * efic)

    def getTheta(self, npass, delay):
        """
        Returns the number of infected individuals in this
        site commuting through the edge that called
        this function.

        npass -- number of individuals leaving the node.
        """
        if delay >= len(self.migInf):
            delay = len(self.migInf) - 1
        lag = -1 - delay
        migInf = 0 if self.migInf == [] else self.migInf[lag]
        #        print "==> ",npass, lag, self.migInf,  self.totpop
        if self.stochtransp == 0:
            theta = npass * migInf / float(self.totpop)  # infectious migrants

        else:  # Stochastic migration
            # print lag, self.migInf
            #            print npass
            try:
                theta = binomial(int(npass), migInf / float(self.totpop))
            except ValueError:  # if npass is less than one or migInf == 0
                theta = 0
            #        print theta
            # Check if site is quarantined
        if self.parentGraph.simstep > self.quarantine[0]:
            self.nQuarantined = npass * self.quarantine[1]
            return theta * (1 - self.quarantine[1]), npass * (1 - self.quarantine[1])
        else:
            return theta, npass

    def getThetaindex(self):
        """
        Returns the Theta index.
        Measures the function of a node, that is the average
        amount of traffic per intersection. The higher theta is,
        the greater the load of the network.
        """
        if self.thidx:
            return self.thidx
        self.thidx = thidx = sum([(i.fmig + i.bmig) / 2. for i in self.edges]) / len(self.parentGraph.site_list)
        return thidx

    def receiveTheta(self, thetai, npass, site):
        """
        Number of infectious individuals arriving from site i
        :param thetai: number of infected passengers
        :param npass: Number of passengers arriving
        :param site: site sending passengers
        :return:
        """
        self.thetalist.append((site, thetai))
        self.passlist.append(npass)

    # def plotItself(self):
    #     """
    #     plot site timeseries
    #     """
    #     a = transpose(array(self.ts))
    #     #figure(int(self.totpop))
    #     figure()
    #     for i in xrange(3):
    #         plot(transpose(a[i]))
    #     title(self.sitename)
    #     legend(('E', 'I', 'S'))
    #     xlabel('time(days)')
    #     savefig(str(self.geocode) + '.png')
    #     close()
    # show()

    def isNode(self):
        """
        find is given site is a node of a graph
        """
        if self.parentGraph:
            return 1
        else:
            return 0

    def getOutEdges(self):
        '''
        return a list of outbound edges
        '''
        if self.outedges:
            return self.outedges
        oe = [e for e in self.edges if self == e.source]
        self.outedges = oe
        return oe

    def getInEdges(self):
        '''
        return a list of outbound edges
        '''
        if self.inedges:
            return self.inedges
        ie = [e for e in self.edges if self == e.dest]
        self.inedges = ie
        return ie

    def getNeighbors(self):
        """
        Returns a dictionary of neighbooring sites as keys,
        and distances as values.
        """
        if not self.isNode():
            return []
        if self.neighbors:
            return self.neighbors
        neigh = {}
        for i in self.edges:
            n = [i.source, i.dest, i.length]
            idx = n.index(self)
            n.pop(idx)
            neigh[n[0]] = n[-1]

        self.neighbors = neigh
        return neigh

    def getDistanceFromNeighbor(self, neighbor):
        """
        Returns the distance in Km from a given neighbor.
        neighbor can be a siteobj object, or a geocode number
        """

        if not self.neighbors:
            self.neighbors = self.getNeighbors()

        if type(neighbor) == type(1):
            nei = [n for n in self.neighbors if int(n.geocode) == neighbor]
            if nei:
                d = [e.length for e in self.edges if nei in e.sites][0]
            else:
                sys.exit('%s is not a neighbor of %s!' % (nei[0].sitename, self.sitename))
        else:
            if neighbor in self.neighbors:
                d = [e.length for e in self.edges if neighbor in e.sites][0]
                # if d == 0:
                # print 'problem determining distance from neighboor'
            else:
                sys.exit('%s is not a neighbor of %s!' % (neighbor.sitename, self.sitename))

        return d

    def getDegree(self):
        """
        Returns the degrees of this site if it is part of a graph.
        The order (degree) of a node is the number of nodes attached to it
        and is a simple, but effective measure of nodal importance.

        The higher its value, the more a node is important in a graph
        as many links converge to it. Hub nodes have a high order,
        while terminal points have an order that can be as low as 1.

        A perfect hub would have its order equal to the summation of
        all the orders of the other nodes in the graph and a perfect
        spoke would have an order of 1.
        
        Returns an integer.
        """
        if not self.isNode():
            return 0
        else:
            return len(self.getNeighbors())

    def doStats(self):
        """
        Calculate indices describing the node and return them in a list.
        """
        self.centrality = self.getCentrality()
        self.degree = self.getDegree()
        self.thidx = self.getThetaindex()
        self.betweeness = self.getBetweeness()

        return [self.centrality, self.degree, self.thidx, self.betweeness]

    def getCentrality(self):
        """
        Also known as closeness. A measure of global centrality, is the
        inverse of the sum of the shortest paths to all other nodes
        in the graph.
        """
        # get position in the distance matrix.
        if self.centrality:
            return self.centrality
        pos = self.parentGraph.site_list.index(self)
        if not self.parentGraph.allPairs.any():
            self.parentGraph.getAllPairs()
        c = 1. / sum(self.parentGraph.allPairs[pos])
        return c

    def getBetweeness(self):
        """
        Is the number of times any node figures in the the shortest path
        between any other pair of nodes.
        """
        if self.betweeness:
            return self.betweeness
        B = 0
        for i in self.parentGraph.shortPathList:
            if not self in i:
                if self in i[2]:
                    B += 1
        return B


class edge:
    """
    Defines an edge connecting two nodes (node source to node dest).
    with attributes given by value.
    """

    def __init__(self, source, dest, fmig=0, bmig=0, Leng=0):
        """
        Main attributes of *Edge*.

        source -- Source site object.

        dest -- Destination site object.

        fmig -- forward migration rate in number of indiv./day.

        bmig -- backward migration rate in number of indiv./day.

        Length -- Length in kilometers of this route
        """
        if not isinstance(source, siteobj):
            raise TypeError('source received a non siteobj class object')
        if not isinstance(dest, siteobj):
            raise TypeError('destination received a non siteobj class object')
        self.dest = dest
        self.source = source
        self.sites = [source, dest]
        self.fmig = float(fmig)  # daily migration from source to destination
        self.bmig = float(bmig)  # daily migration from destination to source
        self.parentGraph = None
        self.length = Leng
        self.delay = 0
        self.ftheta = []  # time series of number of infected individuals travelling forward
        self.btheta = []  # time series of number of infected individuals travelling backwards
        dest.edges.append(self)  # add itself to edge list of dest site
        source.edges.append(self)  # add itself to edge list of source site

    def calcDelay(self):
        """
        calculate the Transportation delay given the speed and length.
        """
        if self.parentGraph.speed > 0:
            self.delay = int(float(self.length) / self.parentGraph.speed)

    def migrate(self):
        """
        Get infectious individuals commuting from source node and inform them to destination.
        this is done for both directions of the edge
        :returns: (ftheta, btheta, fnpass, bnpass)
        """
        # Forward Migration
        ftheta, fnpass = self.source.getTheta(self.fmig, self.delay)
        self.ftheta.append(ftheta)
        self.dest.receiveTheta(ftheta, fnpass, self.source)
        #        print "F -->", theta,npass
        # Backwards Migration
        btheta, bnpass = self.dest.getTheta(self.bmig, self.delay)
        self.btheta.append(btheta)
        self.source.receiveTheta(btheta, bnpass, self.dest)

        return ftheta, btheta, fnpass, bnpass


#        print "B -->", theta,npass


class graph(NX.MultiDiGraph):
    """
    Defines a graph with sites and edges
    """

    def __init__(self, graph_name, digraph=0):
        super().__init__()
        self.name = graph_name
        self.digraph = digraph
        self.site_dict = {}  # geocode as keys
        self.edge_dict = {}  # geocode tuple as key
        self.speed = 0  # speed of the transportation system
        self.simstep = 0  # current step in the simulation
        self.maxstep = 100  # maximum number of steps in the simulation
        self.epipath = []
        self.graphdict = {}
        self.shortPathList = []
        self.parentGraph = self
        self.allPairs = zeros(1)
        self.cycles = None
        self.wienerD = None
        self.meanD = None
        self.diameter = None
        self.length = None
        self.weight = None
        self.iotaidx = None
        self.piidx = None
        self.betaidx = None
        self.alphaidx = None
        self.gammaidx = None
        self.connmatrix = None
        self.shortDistMatrix = None
        self.episize = 0  # total number of people infected
        self.epispeed = []  # new cities pre unit of time
        self.infectedcities = 0  # total number of cities infected.
        self.spreadtime = 0
        self.mediansurvival = None
        self.totVaccinated = 0
        self.totQuarantined = 0
        self.dmap = 0  # draw the map in the background?
        self.printed = 0  # Printed the custom model docstring?

    @property
    def site_list(self):
        return list(self.site_dict.values())

    @property
    def edge_list(self):
        return list(self.edge_dict.values())

    def addSite(self, sitio):
        """
        Adds a site object to the graph.
        It takes a siteobj object as its only argument and returns
        None.
        """

        if not isinstance(sitio, siteobj):
            raise Exception('add_site received a non siteobj instance')
        self.site_dict[sitio.geocode] = sitio
        self.add_node(sitio)
        sitio.parentGraph = self

    def getSite(self, name):
        """Retrieved a site from the graph.

        Given a site's name the corresponding Siteobj
        instance will be returned.

        If multiple sites exist with that name, a list of
        Siteobj instances is returned.

        If only one site exists, the instance is returned.
        None is returned otherwise.
        """

        match = [sitio for sitio in self.site_list if sitio.name() == str(name)]

        l = len(match)
        if l == 1:
            return match[0]
        elif l > 1:
            return match
        else:
            return None

    def addEdge(self, graph_edge):
        """Adds an edge object to the graph.

        It takes a edge object as its only argument and returns
        None.
        """

        if not isinstance(graph_edge, edge):
            raise TypeError('add_edge received a non edge class object')

        if not graph_edge.source.geocode in self.site_dict:
            raise KeyError('Edge source does not belong to the graph')

        if not graph_edge.dest.geocode in self.site_dict:
            raise KeyError('Edge destination does not belong to the graph')
        #        self.edge_list.append(graph_edge)
        self.edge_dict[(graph_edge.source.geocode, graph_edge.dest.geocode)] = graph_edge
        self.add_edge(self.site_dict[graph_edge.source.geocode], self.site_dict[graph_edge.dest.geocode],
                      edgeobj=graph_edge)
        graph_edge.parentGraph = self
        graph_edge.calcDelay()

    def getGraphdict(self):
        """
        Generates a dictionary of the graph for use in the shortest path function.
        """
        G = {}
        for i in self.site_dict.values():
            G[i] = i.getNeighbors()
        self.graphdict = G
        return G

    def getEdge(self, src, dst):
        """
        Retrieved an edge from the graph.

        Given an edge's source and destination the corresponding
        Edge instance will be returned.

        If multiple edges exist with that source and destination,
        a list of Edge instances is returned.

        If only one edge exists, the instance is returned.
        None is returned otherwise.
        """

        match = [edge for edge in self.edge_list if edge.source == src and edge.dest == dst]

        l = len(match)
        if l == 1:
            return match[0]
        elif l > 1:
            return match
        else:
            return None

    def getSiteNames(self):
        """
        returns list of site names for a given graph.
        """
        sitenames = [s.sitename for s in self.site_dict.values()]

        return sitenames

    def getCycles(self):
        """
        The maximum number of independent cycles in a graph.

        This number (u) is estimated by knowing the number of nodes (v),
        links (e) and of sub-graphs (p); u = e-v+p.

        Trees and simple networks will have a value of 0 since they have
        no cycles.

        The more complex a network is, the higher the value of u,
        so it can be used as an indicator of the level of development
        of a transport system.
        """
        u = len(self.edge_list) - len(self.site_list) + 1
        return u

    def shortestPath(self, G, start, end):
        """
        Find a single shortest path from the given start node
        to the given end node.
        The input has the same conventions as self.dijkstra().
        'G' is the graph's dictionary self.graphdict.
        'start' and 'end' are site objects.
        The output is a list of the vertices in order along
        the shortest path.
        """
        try:
            path = NX.shortest_path(self, start, end)
        except NetworkXNoPath:
            path = []
        return path

    def drawGraph(self):
        """
        Draws the network using pylab
        """
        NX.draw(self)

    def getAllPairs(self):
        """
        Returns a distance matrix for the graph nodes where
        the distance is the shortest path. Creates another
        distance matrix where the distances are the lengths of the paths.
        """
        if self.allPairs.any():  # don't run twice
            return self.allPairs
        if self.graphdict:
            g = self.graphdict
        else:
            g = self.getGraphdict()

        d = len(g)
        dm = zeros((d, d), float)
        ap = zeros((d, d), float)
        i = 0
        for sitei in self.nodes:
            j = 0
            for sitej in self.nodes:
                if sitej == sitei:
                    break  # calculates only the lower triangle
                sp = self.shortestPath(g, sitei, sitej)
                lsp = self.getShortestPathLength(sitei, sp)  # length of the shortestpath
                self.shortPathList.append((sitei, sitej, sp, lsp))
                # fill the entire allpairs matrix
                try:
                    ap[i, j] = ap[j, i] = len(sp) - 1
                    dm[i, j] = dm[j, i] = lsp
                except IndexError:
                    pass
                j += 1
            i += 1
        self.shortDistMatrix = dm
        # print ap,dm
        self.allPairs = ap
        return ap

    def getShortestPathLength(self, origin, sp):
        """
        Returns sp Length
        """
        Length = 0
        i = 0
        for s in sp[:-1]:
            Length += s.getDistanceFromNeighbor(sp[i + 1])
            i += 1
        return Length

    def getConnMatrix(self):
        """
        The most basic measure of accessibility involves network connectivity
        where a network is represented as a  connectivity matrix (C1), which
        expresses the connectivity of each node with its adjacent nodes.

        The number of columns and rows in this matrix is equal to the number
        of nodes in the network and a value of 1 is given for each cell where
        this is a connected pair and a value of 0 for each cell where there
        is an unconnected pair. The summation of this matrix provides a very
        basic measure of accessibility, also known as the degree of a node.
        """

        return NX.adjacency_matrix(self)

    def getWienerD(self):
        """
        Returns the Wiener distance for a graph.
        """

        return NX.wiener_index(self)

    def getMeanD(self):
        """
        Returns the mean distance for a graph.
        """
        if self.meanD:
            return self.meanD

        if self.allPairs.any():
            return mean(compress(greater(self.allPairs.flat, 0), self.allPairs.flat))

        return mean(compress(greater(self.getAllPairs().flat, 0), self.getAllPairs().flat))

    def getDiameter(self):
        """
        Returns the diameter of the graph: longest shortest path.
        """
        try:
            return NX.distance_measures.diameter(self)
        except NetworkXError:
            return np.inf

    def getIotaindex(self):
        """
        Returns the Iota index of the graph

        Measures the ratio between the network and its weighed vertices.
        It considers the structure, the length and the function
        of a graph and it is mainly used when data about traffic
        is not available.

        It divides the length of a graph (L(G)) by its weight (W(G)).
        The lower its value, the more efficient the network is.
        This measure is based on the fact that an intersection
        (represented as a node) of a high order is able to handle
        large amounts of traffic.

        The weight of all nodes in the graph (W(G)) is the summation
        of each node's order (o) multiplied by 2 for all orders above 1.
        """

        iota = self.getLength() / self.getWeight()
        return iota

    def getWeight(self):
        """
        The weight of all nodes in the graph (W(G)) is the summation
        of each node's order (o) multiplied by 2 for all orders above 1.
        """
        degrees = [i.getDegree() for i in self.site_dict.values()]
        W = sum([i * 2 for i in degrees if i > 1]) + sum([i for i in degrees if i < 2])
        return float(W)

    def getLength(self):
        """
        Sum of the length in kilometers of all edges in the graph.
        """
        L = sum([i.length for i in self.edge_list])
        return float(L)

    def getPiIndex(self):
        """
        Returns the Pi index of the graph.

        The relationship between the total length of the graph L(G)
        and the distance along the diameter D(d).

        It is labeled as Pi because of its similarity with the
        real Pi (3.14), which is expressing the ratio between
        the circumference and the diameter of a circle.

        A high index shows a developed network. It is a measure
        of distance per units of diameter and an indicator of
        the  shape of a network.
        """
        if self.length:
            l = self.length
        else:
            l = self.getLength()

        lsp = [len(i[2]) for i in self.shortPathList]  # list of lenghts of shortest paths.
        lpidx = lsp.index(max(lsp))  # position of the longest sp.
        lp = self.shortPathList[lpidx][2]  # longest shortest path
        Dd = 0
        for i in range(len(lp) - 1):  # calculates distance in km along lp
            Dd += lp[i].getDistanceFromNeighbor(lp[i + 1])

        # pi = l/self.getDiameter()
        pi = l / Dd
        return float(pi)

    def getBetaIndex(self):
        """
        The Beta index
        measures the level of connectivity in a graph and is
        expressed by the relationship between the number of
        links (e) over the number of nodes (v).

        Trees and simple networks have Beta value of less than one.
        A connected network with one cycle has a value of 1.
        More complex networks have a value greater than 1.
        In a network with a fixed number of nodes, the higher the
        number of links, the higher the number of paths possible in
        the network. Complex networks have a high value of Beta.
        """
        B = len(self.edge_dict) / float(len(self.site_dict))
        return B

    def getAlphaIndex(self):
        """
        The Alpha index is a measure of connectivity which evaluates
        the number of cycles in a graph in comparison with the maximum
        number of cycles. The higher the alpha index, the more a network
        is connected. Trees and simple networks will have a value of 0.
        A value of 1 indicates a completely connected network.

        Measures the level of connectivity independently of the number of
        nodes. It is very rare that a network will have an alpha value of 1,
        because this would imply very serious redundancies.
        """
        nsites = float(len(self.site_dict))
        A = self.getCycles() / (2. * nsites - 5)
        return A

    def getGammaIndex(self):
        """
        The Gamma index is a A measure of connectivity that considers
        the relationship between the number of observed links and the
        number of possible links.

        The value of gamma is between 0 and 1 where a value of 1
        indicates a completely connected network and would be extremely
        unlikely in reality. Gamma is an efficient value to measure
        the progression of a network in time.
        """
        nedg = float(len(self.edge_dict))
        nsites = float(len(self.site_dict))
        G = nedg / 3 * (nsites - 2)
        return G

    def doStats(self):
        """
        Generate the descriptive stats about the graph.
        """
        self.allPairs = self.getAllPairs()
        self.cycles = self.getCycles()
        self.wienerD = self.getWienerD()
        self.meanD = self.getMeanD()
        self.diameter = self.getDiameter()
        self.length = self.getLength()
        self.weight = self.getWeight()
        self.iotaidx = self.getIotaindex()
        self.piidx = self.getPiIndex()
        self.betaidx = self.getBetaIndex()
        self.alphaidx = self.getAlphaIndex()
        self.gammaidx = self.getGammaIndex()
        self.connmatrix = self.getConnMatrix()

        return [self.allPairs, self.cycles, self.wienerD, self.meanD, self.diameter, self.length,
                self.weight, self.iotaidx, self.piidx, self.betaidx, self.alphaidx, self.gammaidx,
                self.connmatrix]

    # def plotDegreeDist(self, cum=False):
    #     """
    #     Plots the Degree distribution of the graph
    #     maybe cumulative or not.
    #     """
    #     nn = len(self.site_dict)
    #     ne = len(self.edge_dict)
    #     deglist = [i.getDegree() for i in self.site_dict.itervalues()]
    #     if not cum:
    #         hist(deglist)
    #         title('Degree Distribution (N=%s, E=%s)' % (nn, ne))
    #         xlabel('Degree')
    #         ylabel('Frequency')
    #     else:
    #         pass
    #     savefig('degdist.png')
    #     close()

    def getMedianSurvival(self):
        """
        Returns the time taken by the epidemic to reach 50% of the nodes.
        """
        n = len(self.site_dict)
        try:
            median = self.epipath[int(n / 2)][0]
        except:  # In the case the epidemic does not reach 50% of nodes
            median = 'NA'
        return median

    def getTotVaccinated(self):
        """
        Returns the total number of vaccinated.
        """
        tot = sum([i.nVaccinated for i in self.site_dict.values()])
        return tot

    def getTotQuarantined(self):
        """
        Returns the total number of quarantined individuals.
        """
        tot = sum([i.nQuarantined for i in self.site_dict.values()])
        return tot

    def getEpistats(self):
        """
        Returns a list of all epidemiologically related stats.
        """
        self.episize = self.getEpisize()
        self.epispeed = self.getEpispeed()
        self.infectedcities = self.getInfectedCities()
        self.spreadtime = 0  # self.getSpreadTime()
        self.mediansurvival = self.getMedianSurvival()
        self.totVaccinated = self.getTotVaccinated()
        self.totQuarantined = self.getTotQuarantined()

        return [self.episize, self.epispeed, self.infectedcities,
                self.spreadtime, self.mediansurvival, self.totVaccinated, self.totQuarantined]

    def getInfectedCities(self):
        """
        Returns the number of infected cities.
        """
        res = len(self.epipath)
        return res

    def getEpisize(self):
        """
        Returns the size of the epidemic
        """
        N = sum([site.totalcases for site in self.site_dict.values()])

        return N

    def getEpispeed(self):
        """
        Returns the epidemic spreading speed.
        """
        tl = [i[0] for i in self.epipath]
        nspt = []
        for j in range(self.simstep):
            nspt.append(tl.count(j))  # new sites per time step
            # Speed = [nspt[i+1]-nspt[i] for i in range(len(nspt))]
        return nspt

    def getSpreadTime(self):
        """
        Returns the duration of the epidemic in units of time.
        """
        tl = [i[0] for i in self.epipath]
        if not tl:
            dur = 'NA'
        else:
            dur = tl[-1] - tl[0]
        return dur

    def save_topology(self, pa):
        """
        Saves graph structure to a graphml file for visualization
        :Parameters:
        :pa: path in which to save the graphml file
        """

        g = NX.MultiDiGraph()
        for gc, n in self.site_dict.items():
            g.add_node(gc, name=str(n.sitename), pos=n.pos)
        for ed, e in self.edge_dict.items():
            g.add_edge(ed[0], ed[1], weight=e.fmig + e.bmig)
        # print(g.nodes)
        # NX.write_graphml_lxml(g, pa)
        NX.write_gml(g, pa.replace('gexf', 'gml'))
        nl = json_graph.node_link_data(g)
        jsonpath = pa.replace('gexf', 'json')
        with open(jsonpath, 'w') as f:
            json.dump(nl, f)

    def resetStats(self):
        """
        Resets all graph related stats
        """
        self.allPairs = None
        self.cycles = None
        self.wienerD = None
        self.meanD = None
        self.diameter = None
        self.length = None
        self.weight = None
        self.iotaidx = None
        self.piidx = None
        self.betaidx = None
        self.alphaidx = None
        self.gammaidx = None


class priorityDictionary(dict):
    def __init__(self):
        '''
        by David Eppstein.
        <http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/117228>
        Initialize priorityDictionary by creating binary heap
        of pairs (value,key).  Note that changing or removing a dict entry will
        not remove the old pair from the heap until it is found by smallest() or
        until the heap is rebuilt.
        '''
        self.__heap = []
        dict.__init__(self)

    def smallest(self):
        '''
        Find smallest item after removing deleted items from heap.
        '''
        if len(self) == 0:
            raise IndexError("smallest of empty priorityDictionary")
        heap = self.__heap
        while heap[0][1] not in self or self[heap[0][1]] != heap[0][0]:
            lastItem = heap.pop()
            insertionPoint = 0
            while 1:
                smallChild = 2 * insertionPoint + 1
                if smallChild + 1 < len(heap) and \
                        heap[smallChild] > heap[smallChild + 1]:
                    smallChild += 1
                if smallChild >= len(heap) or lastItem <= heap[smallChild]:
                    heap[insertionPoint] = lastItem
                    break
                heap[insertionPoint] = heap[smallChild]
                insertionPoint = smallChild
        return heap[0][1]

    def __iter__(self):
        '''
        Create destructive sorted iterator of priorityDictionary.
        '''

        def iterfn():
            while len(self) > 0:
                x = self.smallest()
                yield x
                del self[x]

        return iterfn()

    def __setitem__(self, key, val):
        '''
        Change value stored in dictionary and add corresponding
        pair to heap.  Rebuilds the heap if the number of deleted
        items grows too large, to avoid memory leakage.
        '''
        dict.__setitem__(self, key, val)
        heap = self.__heap
        if len(heap) > 2 * len(self):
            self.__heap = [(v, k) for k, v in self.items()]
            self.__heap.sort()  # builtin sort likely faster than O(n) heapify
        else:
            newPair = (val, key)
            insertionPoint = len(heap)
            heap.append(None)
            while insertionPoint > 0 and \
                    newPair < heap[(insertionPoint - 1) // 2]:
                heap[insertionPoint] = heap[(insertionPoint - 1) // 2]
                insertionPoint = (insertionPoint - 1) // 2
            heap[insertionPoint] = newPair

    def update(self, other):
        for key in other.keys():
            self[key] = other[key]

    def setdefault(self, key, val):
        '''Reimplement setdefault to call our customized __setitem__.'''
        if key not in self:
            self[key] = val
        return self[key]

    # ---main----------------------------------------------------------------------------

    # if __name__ == '__main__':
    #    sitioA = siteobj("Penedo",2000)
    #    sitioB = siteobj("Itatiaia",3020)
    #    linhaA = edge(sitioA,sitioB,4)
    #    sitioA.createModel((.3,.3,.3),(1,1))
    #   sitioA.runModel()
    # lista_de_sitios = (i=siteobj(10) for i = range(10))
