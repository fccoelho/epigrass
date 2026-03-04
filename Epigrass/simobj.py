"""
This Module contains the definitions of objects for spatial simulation on geo reference spaces.
"""

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
redisclient = redis.Redis(host="localhost", port=6379)
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
        self.totalcases = 0  # Cumulative total cases up to current time step
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

    def createModel(self, modtype="", modelname="name", v=[], bi=None, bp=None):
        """
        Creates a model of type modtype and defines its initial parameters.
        init -- initial conditions for the state variables tuple with fractions of the total
        population in each category (state variable).
        par -- initial values for the parameters.
        v -- List of extra variables passed in the sites files
        bi, bp -- dictionaries containing all the inits and parms defined in the .epg model
        """
        # Init = init  # deprecated
        self.modename = modelname
        N = self.totpop
        self.modtype = bytes(modtype, "utf8")
        self.values = v
        self.bi = bi
        self.bp = bp
        if modtype in ["Custom", "custom"]:
            if CustomModel is None:
                raise ImportError(
                    "You have to Create a CustomModel.py file before you can select\nthe Custom model type"
                )
            self.model = CustomModel.Model
            self.vnames = CustomModel.vnames
        else:
            self.model = models.Epimodel(self.geocode, self.modtype)
            self.vnames = models.vnames[modtype]
        try:
            # self.ts = [[bi[vn.lower()] for vn in self.vnames]]
            self.ts.append(list(bi.values()))  # This is fine since bi is an OrderedDict
        except KeyError as ke:
            if self.vnames == ["Exposed", "Infectious", "Susceptible"]:
                self.ts = [[bi[vn] for vn in ["e", "i", "s"]]]
            else:
                raise KeyError("%s" % ke)
        self.bp["vaccineNow"] = 0
        self.bp["vaccov"] = 0

    #        self.model = popmodels(self.id,type=modtype,v=self.values,bi = self.bi, bp = self.bp)

    def runModel(self, parallel=True):
        """
        Iterate the model
        :Parameters:
        - parallel: run in a separate process if true
        """

        if self.parentGraph.simstep in self.vaccination[0]:
            self.vaccineNow = 1
            self.vaccov = float(
                self.vaccination[1][self.vaccination[0].index(self.parentGraph.simstep)]
            )
            self.bp["vaccineNow"] = 1
            self.bp["vaccov"] = self.vaccov
        else:
            self.bp["vaccineNow"] = 0
        if self.thetalist != []:
            theta = sum([i[1] for i in self.thetalist])
            self.infector = dict(
                [i for i in self.thetalist if i[1] > 0]
            )  # Only those that contribute at least one infected individual
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
        if parallel:
            pipe = redisclient.pipeline()
            pipe.set("simstep", simstep)
            pipe.set("{}:totpop".format(self.geocode), totpop)
            # pipe.rpush("{}:inits".format(self.geocode), str(inits))
            pipe.rpush("{}:ts".format(self.geocode), json.dumps(inits))
            pipe.set("{}:npass".format(self.geocode), float(npass))
            pipe.set("{}:theta".format(self.geocode), int(nan_to_num(theta)))
            pipe.hset("{}:bi".format(self.geocode), mapping=self.bi)
            pipe.hset("{}:bp".format(self.geocode), mapping=self.bp)
            pipe.execute()
            r = PO.apply_async(self.model, args=(), callback=self.handle)
        else:
            res = self.model(
                inits, simstep, totpop, theta, npass, self.bi, self.bp, self.values
            )
            self.handle(res)
            r = None

        self.thetahist.append(theta)  # keep a record of infected passenger arriving
        # Clear arrival lists for the next time step
        self.thetalist = []
        self.passlist = []
        return r

    #        state, Lpos, migInf = self.model.step(inits=self.ts[-1],simstep=simstep,totpop=self.totpop,theta=theta,npass=npass)

    def handle(self, res):
        """
        Processes the output of a step updating simulation statistics
        :param res: Tuple with the output of the simulation model
        """
        state, Lpos, migInf = res

        self.ts.append(state)
        self.totalcases += Lpos
        self.incidence.append(Lpos)

        if not self.infected:
            if Lpos > 0:
                self.infected = self.parentGraph.simstep
                self.parentGraph.epipath.append(
                    (self.parentGraph.simstep, self.geocode, self.infector)
                )
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
        self.thidx = thidx = sum([(i.fmig + i.bmig) / 2.0 for i in self.edges]) / len(
            self.parentGraph.site_list
        )
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
        """
        return a list of outbound edges
        """
        if self.outedges:
            return self.outedges
        oe = [e for e in self.edges if self == e.source]
        self.outedges = oe
        return oe

    def getInEdges(self):
        """
        return a list of outbound edges
        """
        if self.inedges:
            return self.inedges
        ie = [e for e in self.edges if self == e.dest]
        self.inedges = ie
        return ie

    def getNeighbors(self):
        """
        Returns a dictionary of neighboring sites as keys and distances as values.

        Uses NetworkX's efficient neighbor iteration instead of manual edge traversal.
        Results are cached in self.neighbors for performance.

        Returns:
        --------
        dict : {siteobj: distance_in_km} mapping of neighbors to distances
        """
        if not self.isNode():
            return {}
        if self.neighbors:
            return self.neighbors

        neigh = {}

        # Use NetworkX's optimized neighbor iteration
        # This is more efficient than iterating through all edges
        for neighbor in self.parentGraph.neighbors(self):
            # Get edge data between self and neighbor
            # For MultiDiGraph, there might be multiple edges
            edge_data = self.parentGraph.get_edge_data(self, neighbor)

            if edge_data:
                # edge_data is a dict: {edge_key: {edge_attributes}}
                # Get the first edge (or we could aggregate parallel edges)
                first_edge_key = list(edge_data.keys())[0]
                edge_attrs = edge_data[first_edge_key]

                # Get the custom edge object stored in 'edgeobj' attribute
                edge_obj = edge_attrs.get("edgeobj")

                if edge_obj and hasattr(edge_obj, "length"):
                    neigh[neighbor] = edge_obj.length
                else:
                    # If no length available, use 0 or topological distance
                    neigh[neighbor] = 0

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
                sys.exit(
                    "%s is not a neighbor of %s!" % (nei[0].sitename, self.sitename)
                )
        else:
            if neighbor in self.neighbors:
                d = [e.length for e in self.edges if neighbor in e.sites][0]
                # if d == 0:
                # print 'problem determining distance from neighboor'
            else:
                sys.exit(
                    "%s is not a neighbor of %s!" % (neighbor.sitename, self.sitename)
                )

        return d

    def getDegree(self):
        """
        Returns the degree of this site if it is part of a graph.

        The degree is the number of edges connected to the node.
        For directed graphs (MultiDiGraph), this is the sum of
        in-degree and out-degree.

        The higher the degree, the more important the node in the network.
        Hub nodes have high degree, while terminal points have degree as low as 1.

        Uses NetworkX's O(1) cached degree computation for efficiency.

        Returns:
        --------
        int : The degree of this node
        """
        if not self.isNode():
            return 0

        # Use NetworkX's cached degree (O(1) operation)
        # For MultiDiGraph, this returns total degree (in + out)
        return self.parentGraph.degree(self)

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
        Closeness centrality: measures how close a node is to all other nodes.

        Defined as the reciprocal of the sum of the shortest path distances
        from the node to all other reachable nodes in the graph.

        Higher values indicate more central nodes (shorter average distance to others).
        Uses NetworkX's closeness_centrality which implements the Wasserman-Faust
        formula for proper handling of disconnected graphs.

        Returns:
        --------
        float : Closeness centrality value (0-1 range)
        """
        if self.centrality is not None:
            return self.centrality

        # Use NetworkX's closeness centrality
        # This is more efficient and handles disconnected components properly
        # using the Wasserman-Faust formula
        self.centrality = NX.closeness_centrality(self.parentGraph, self)

        return self.centrality

    def getBetweeness(self):
        """
        Betweenness centrality measures how often a node appears on
        shortest paths between other pairs of nodes.

        Nodes with high betweenness act as bridges or bottlenecks in the network.
        This is important for understanding disease transmission pathways.

        Uses NetworkX's betweenness_centrality for efficient computation.
        For large graphs (>1000 nodes), uses sampling for performance.

        Returns absolute (non-normalized) betweenness values.

        Returns:
        --------
        float : Betweenness centrality value (absolute count)
        """
        if self.betweeness is not None:
            return self.betweeness

        # Determine if we should use sampling for large graphs
        n_nodes = len(self.parentGraph.site_dict)
        sample_size = min(100, n_nodes) if n_nodes > 1000 else None

        # Use NetworkX's betweenness centrality
        # normalized=False to get absolute counts (not 0-1 range)
        # endpoints=False to exclude source/target nodes from path count
        betweenness_dict = NX.betweenness_centrality(
            self.parentGraph,
            k=sample_size,  # None for exact, int for sampling
            normalized=False,
            endpoints=False,
            weight=None,  # Use topological distance
        )

        self.betweeness = betweenness_dict.get(self, 0)
        return self.betweeness


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
            raise TypeError("source received a non siteobj class object")
        if not isinstance(dest, siteobj):
            raise TypeError("destination received a non siteobj class object")
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
        self.shortPathList = []
        self.parentGraph = self
        self.allPairs = zeros(1)
        self.shortDistMatrix = zeros(1)  # Physical distance matrix (lazy computation)
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
            raise Exception("add_site received a non siteobj instance")
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
            raise TypeError("add_edge received a non edge class object")

        if not graph_edge.source.geocode in self.site_dict:
            raise KeyError("Edge source does not belong to the graph")

        if not graph_edge.dest.geocode in self.site_dict:
            raise KeyError("Edge destination does not belong to the graph")
        #        self.edge_list.append(graph_edge)
        self.edge_dict[(graph_edge.source.geocode, graph_edge.dest.geocode)] = (
            graph_edge
        )
        self.add_edge(
            self.site_dict[graph_edge.source.geocode],
            self.site_dict[graph_edge.dest.geocode],
            edgeobj=graph_edge,
        )
        graph_edge.parentGraph = self
        graph_edge.calcDelay()

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

        match = [
            edge for edge in self.edge_list if edge.source == src and edge.dest == dst
        ]

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
        Uses NetworkX's shortest_path algorithm.

        Parameters:
        -----------
        G : Unused parameter (kept for backward compatibility)
        start : site object
            Starting node
        end : site object
            Ending node

        Returns:
        --------
        list : Vertices in order along the shortest path, or empty list if no path exists
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
        the distance is the shortest path length (topological/hops).

        Uses NetworkX's all_pairs_shortest_path_length for efficient computation.
        Results are cached in self.allPairs.

        For physical distances (kilometers), use getAllPairsPhysical() instead.

        Returns:
        --------
        numpy.ndarray : Matrix of shortest path lengths (number of hops)
        """
        if self.allPairs.any():  # don't run twice
            return self.allPairs

        # Use NetworkX's efficient all-pairs shortest path length
        lengths = dict(NX.all_pairs_shortest_path_length(self))

        d = len(self.nodes)
        ap = np.zeros((d, d), float)

        nodes_list = list(self.nodes)
        node_to_idx = {node: i for i, node in enumerate(nodes_list)}

        for i, node_i in enumerate(nodes_list):
            if node_i in lengths:
                for node_j, length in lengths[node_i].items():
                    j = node_to_idx[node_j]
                    ap[i, j] = length

        self.allPairs = ap
        return ap

    def getAllPairsPhysical(self):
        """
        Returns a distance matrix with physical distances (in kilometers)
        along the shortest paths between all node pairs.

        This method is computationally expensive as it requires reconstructing
        actual paths and summing edge lengths. It is computed lazily (on-demand)
        and cached in self.shortDistMatrix.

        Note: This method only makes sense if edges have 'length' attributes.

        Returns:
        --------
        numpy.ndarray : Matrix of physical distances (km) along shortest paths
                        inf if no path exists
        """
        # Check cache
        if hasattr(self, "shortDistMatrix") and self.shortDistMatrix.any():
            return self.shortDistMatrix

        d = len(self.nodes)
        dm = np.full((d, d), np.inf)  # Initialize with infinity

        nodes_list = list(self.nodes)
        node_to_idx = {node: i for i, node in enumerate(nodes_list)}

        # Diagonal is 0 (distance to self)
        np.fill_diagonal(dm, 0)

        # For each pair of nodes, find shortest path and sum edge lengths
        for i, source in enumerate(nodes_list):
            try:
                # Get shortest paths to all other nodes from source
                paths = NX.single_source_shortest_path(self, source)

                for target, path in paths.items():
                    if source == target:
                        continue

                    j = node_to_idx[target]

                    # Sum physical distances along the path
                    physical_dist = 0.0
                    for k in range(len(path) - 1):
                        node1, node2 = path[k], path[k + 1]

                        # Get edge data
                        edge_data = self.get_edge_data(node1, node2)
                        if edge_data:
                            # Take first edge if multiple parallel edges exist
                            first_edge_key = list(edge_data.keys())[0]
                            edge_obj = edge_data[first_edge_key].get("edgeobj")

                            if edge_obj and hasattr(edge_obj, "length"):
                                physical_dist += edge_obj.length

                    dm[i, j] = physical_dist

            except (NetworkXNoPath, NetworkXError):
                # Keep infinity for unreachable nodes
                continue

        # Cache result
        self.shortDistMatrix = dm
        return dm

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

        return mean(
            compress(greater(self.getAllPairs().flat, 0), self.getAllPairs().flat)
        )

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

        Pi = L(G) / D(d)

        Where:
        - L(G) = total length of all edges in the graph
        - D(d) = physical distance along the longest shortest path (diameter)

        A high index shows a developed network with many alternative paths.
        Similar to the mathematical Pi (3.14) which relates circumference to diameter.

        Returns:
        --------
        float : Pi index value
        """
        if self.piidx is not None:
            return self.piidx

        # Get total graph length
        if self.length:
            l = self.length
        else:
            l = self.getLength()

        if l == 0:
            return 0.0

        try:
            # Find the diameter path (longest shortest path)
            # Use NetworkX to find all shortest paths efficiently
            diameter_path = None
            max_hops = 0

            nodes_list = list(self.nodes)

            # Check all pairs to find the longest shortest path
            for i, source in enumerate(nodes_list):
                try:
                    # Get shortest path lengths from source to all other nodes
                    lengths = NX.single_source_shortest_path_length(self, source)
                    if lengths:
                        max_from_source = max(lengths.values())
                        if max_from_source > max_hops:
                            max_hops = max_from_source
                            # Find which node has the max length
                            target = max(lengths, key=lengths.get)
                            diameter_path = NX.shortest_path(self, source, target)
                except (NetworkXNoPath, NetworkXError):
                    continue

            if diameter_path is None or len(diameter_path) < 2:
                self.piidx = 0.0
                return 0.0

            # Calculate physical distance along diameter path
            Dd = 0.0
            for i in range(len(diameter_path) - 1):
                node1, node2 = diameter_path[i], diameter_path[i + 1]

                # Get edge data between consecutive nodes
                edge_data = self.get_edge_data(node1, node2)
                if edge_data:
                    # MultiDiGraph: edge_data is dict of {edge_key: attributes}
                    # Take first edge (or could sum all parallel edges)
                    first_edge_key = list(edge_data.keys())[0]
                    edge_obj = edge_data[first_edge_key].get("edgeobj")

                    if edge_obj and hasattr(edge_obj, "length"):
                        Dd += edge_obj.length

            if Dd == 0:
                self.piidx = 0.0
                return 0.0

            pi = l / Dd
            self.piidx = float(pi)
            return self.piidx

        except Exception as e:
            # If calculation fails for any reason, return 0
            # Log this in production: logger.warning(f"Pi index calculation failed: {e}")
            self.piidx = 0.0
            return 0.0

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
        A = self.getCycles() / (2.0 * nsites - 5)
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

        Computes both graph-level statistics and node-level centrality measures.
        Uses batch computation for efficiency.
        """
        # Compute all centralities at once (more efficient than per-node)
        self.computeAllCentralities()

        # Compute graph-level statistics
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

        return [
            self.allPairs,
            self.cycles,
            self.wienerD,
            self.meanD,
            self.diameter,
            self.length,
            self.weight,
            self.iotaidx,
            self.piidx,
            self.betaidx,
            self.alphaidx,
            self.gammaidx,
            self.connmatrix,
        ]

    def computeAllCentralities(self, sample_size=None):
        """
        Compute centrality measures for all nodes at once.

        This is more efficient than computing centrality for each node individually,
        as NetworkX can optimize graph traversals when computing for all nodes.

        Parameters:
        -----------
        sample_size : int, optional
            For betweenness centrality, use random sampling of k nodes.
            If None and graph has >1000 nodes, automatically uses 100.
            Set to False to force exact computation regardless of graph size.

        Returns:
        --------
        dict : {
            'closeness': {node: closeness_value, ...},
            'betweenness': {node: betweenness_value, ...}
        }

        Example:
        --------
        >>> g.computeAllCentralities()
        >>> # Now all nodes have cached centrality values
        >>> for node in g.site_dict.values():
        ...     print(f"{node.sitename}: {node.centrality:.3f}")
        """
        # Determine sampling strategy for betweenness
        n_nodes = len(self.site_dict)

        if sample_size is None:
            # Auto-sample for large graphs
            sample_k = min(100, n_nodes) if n_nodes > 1000 else None
        elif sample_size is False:
            # Force exact computation
            sample_k = None
        else:
            # Use specified sample size
            sample_k = min(sample_size, n_nodes)

        # Compute closeness centrality for all nodes at once
        closeness = NX.closeness_centrality(self)

        # Compute betweenness centrality for all nodes at once
        betweenness = NX.betweenness_centrality(
            self, k=sample_k, normalized=False, endpoints=False
        )

        # Assign to individual nodes
        for node in self.site_dict.values():
            node.centrality = closeness.get(node, 0)
            node.betweeness = betweenness.get(node, 0)

        return {"closeness": closeness, "betweenness": betweenness}

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
            median = "NA"
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

        return [
            self.episize,
            self.epispeed,
            self.infectedcities,
            self.spreadtime,
            self.mediansurvival,
            self.totVaccinated,
            self.totQuarantined,
        ]

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
            dur = "NA"
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
        NX.write_gml(g, pa.replace("gexf", "gml"))
        nl = json_graph.node_link_data(g)
        jsonpath = pa.replace("gexf", "json")
        with open(jsonpath, "w") as f:
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

    # ---main----------------------------------------------------------------------------

    # if __name__ == '__main__':
    #    sitioA = siteobj("Penedo",2000)
    #    sitioB = siteobj("Itatiaia",3020)
    #    linhaA = edge(sitioA,sitioB,4)
    #    sitioA.createModel((.3,.3,.3),(1,1))
    #   sitioA.runModel()
    # lista_de_sitios = (i=siteobj(10) for i = range(10))
