"""
This module generates a report of the network simulation model
using LaTeX.
"""

import os, sys, string, matplotlib, codecs
from time import time, ctime
import pweave
import datetime

# matplotlib.use("Agg")

from pylab import *
# from matplotlib.mlab import *

header = """
"""


class Report:
    """
    Generates reports in pdf format.
    Takes as input arg. a simulation object.
    """

    def __init__(self, simulation):
        self.workdir = os.getcwd()

        self.sim = simulation
        self.encoding = self.sim.encoding
        if self.encoding == 'latin-1':
            enc = 'latin1'
        elif self.encoding == 'utf-8':
            enc = 'utf8'
        self.header = r"""
        """

    def genNetTitle(self):
        """
        Generates title section of the preamble from 
        data extracted from the simulation.
        """
        modname = self.sim.modelName
        title = f"""
% Model {modname} Network Report
% John Doe
% {datetime.date.today()}
    

        **Abstract**
        Edit the report.pmd file and add your model's description here.
        
"""

        return title

    def genEpiTitle(self):
        """
        Generates title section of the preamble from 
        data extracted from the simulation.
        """
        modname = self.sim.modelName
        title = f"""
        % Model {modname} Epidemiological Report
        % John Doe
        % {datetime.date.today()}


                **Abstract**
                Edit the report.pmd file and add your model's description here.

        """

        return title

    def genFullTitle(self):
        """
        Generates title section of the preamble from 
        data extracted from the simulation.
        """
        modname = self.sim.modelName
        title = f"""
        % Model {modname} Full Report
        % John Doe
        % {datetime.date.today()}


                **Abstract**
                Edit the report.pmd file and add your model's description here.

        """
        return title

    def graphDesc(self):
        """
        Generates the Graph description section.
        """
        stats = tuple(self.sim.g.doStats())
        nodd = sum([1 for i in self.sim.g.site_list if len(i.neighbors) % 2 != 0])
        if nodd:  # check if Graph is Eulerian and/or traversable
            Eul = 'No'
            if nodd == 2:
                Trav = 'Yes'
            else:
                Trav = 'No'
        else:
            Eul = 'Yes'
        pass

        nnodes = len(self.sim.g.site_list)
        nedges = len(self.sim.g.edge_list)
        deglist = [len(i.neighbors) for i in self.sim.g.site_list]
        # check if graph is hamiltonian
        if nnodes >= 3:
            if min(deglist) >= nnodes / 2.:
                Ham = 'Yes'
            else:
                Ham = 'Possibly'
        else:
            Ham = 'Yes'

        matrix = f"""
## General Network Analyses
The figure below contains a simple drawing of your graph. If your network 
is not very complex,it can help you to verify if the topology specified corresponds to
your expectations.
```python
self.sim.g.drawGraph()
```
## Network Descriptive Statistics
In this section you will find quantitative descriptors and plots 
that will help you analyze you network.

### Basic statistics

 - **Order (Number of Nodes):** {nnodes}
 - **Size (Number of Edges):** {nedges}
 - **Eulerian:** {Eul}
 - **Traversable:** {Trav}
 - **Hamiltonian:** {Ham}



## Distance matrix
The distance Matrix represents the number of edges separating any
pair of nodes via the shortest path between them. 

```python
hist(stats[0].flat, normed=1)
title('Shortest paths distribution')
```


## Adjacencyy Matrix
The most basic measure of accessibility involves network connectivity
where a network is represented as a connectivity matrix(below), which 
expresses the connectivity of each node with its adjacent nodes. 

The number of columns and rows in this matrix is equal to the number 
of nodes in the network and a value of 1 is given for each cell where 
this is a connected pair and a value of 0 for each cell where there 
is an unconnected pair. The summation of this matrix provides a very 
basic measure of accessibility, also known as the degree of a node.

```python
pcolor(stats[12])
title('Adjacency Matrix')
colorbar()
```
            
"""
        indices = f"""
## Number of Cycles
The maximum number of independent cycles in a graph.
This number ($u$) is estimated by knowing the number of nodes ($v$), 
links ($e$) and of sub-graphs ($p$); $u = e-v+p$.

Trees and simple networks will have a value of 0 since they have 
no cycles. 
The more complex a network is, the higher the value of u, 
so it can be used as an indicator of the level of development 
of a transport system.

Cycles(u) $={stats[1]}$

## Wiener Distance
The Wiener distance is the sum of all the shortest distances in the network.

Wiener's D $={stats[2]}$

## Mean Distance
The mean distance of a network is the mean of of the set of shortest paths, 
excluding the 0-length paths.""" +\
r"""
$\bar{D}="""+f'{stats[3]}$' + \
fr"""
## Network Diameter
The diameter of a network is the longest element of the shortest paths set.

$D(N)={stats[4]}$
## Length of the Network
The length of a network is the sum in metric units (e.g., km) of all the edges in the network.

$L(N)={stats[5]}$
## Weight of the Network
The weight of a network is the weight of all nodes in the graph ($W(N)$), which is the summation 
of each node's order ($o$) multiplied by 2 for all orders above 1.

$W(N)={stats[6]}$
## Iota ($\iota$) Index
The Iota index measures the ratio between the network and its weighed vertices. 
It considers the structure, the length and the function 
of a network and it is mainly used when data about traffic 
is not available. 

It divides the length of a network (L(N)) by its weight (W(N)). 
The lower its value, the more efficient the network is. 
This measure is based on the fact that an intersection 
(represented as a node) of a high order is able to handle 
large amounts of traffic. 

The weight of all nodes in the network (W(N)) is the summation 
of each node's order (o) multiplied by 2 for all orders above 1.
""" +\
r"""
$\iota=\frac{L(N)}{W(N)}="""+f'{stats[7]}$'+\
r"""        
\subsection{Pi ($\Pi$) Index}
The Pi index represents the relationship between the 
total length of the network L(N)
and the distance along the diameter D(d). 

It is labeled as Pi because of its similarity with the 
trigonometric $\Pi$ (3.14), which is expressing the ratio between 
the circumference and the diameter of a circle. 

A high index shows a developed network. It is a measure 
of distance per units of diameter and an indicator of 
the  shape of a network.
""" +\
fr"""
$\Pi=L(N)/D(d)={stats[8]}$
## Beta ($\beta$) Index
The Beta index
measures the level of connectivity in a network and is 
expressed by the relationship between the number of 
edges (e) over the number of nodes (v). 

Trees and simple networks have Beta value of less than one. 
A connected network with one cycle has a value of 1. 
More complex networks have a value greater than 1. 
In a network with a fixed number of nodes, the higher the 
number of links, the higher the number of paths possible in 
the network. Complex networks have a high value of Beta.

$\beta = {stats[10]}$"""
        section = matrix + indices
        return section


    def siteReport(self, geoc):
        """
        Puts together a report for a given site.
        """
        site = None
        for i in self.sim.g.site_list:
            if int(i.geocode) == int(geoc):
                site = i
        if not site:
            sys.exit("Wrong Geocode specified in the siteRep list")

        stats = site.doStats()
        name = [site.sitename]

        section = fr"""
# {name}
## Centrality
$$C={stats[0]}$$
## Degree
$$D={stats[1]}$$
## Theta Index
$$\theta={stats[2]}$$
## Betweeness 
$$B={stats[3]}$$
```python
site.doStats()
```
        """
        return section


    def genSiteEpi(self, geoc):
        """
        Generate epidemiological reports at the site level.
        """
        site = None
        for i in self.sim.g.site_list:
            if int(i.geocode) == int(geoc):
                site = i
        if not site:
            sys.exit("Wrong Geocode specified in the siteRep list")
        name = site.sitename
        incidence = site.incidence
        totcases = site.totalcases
        cuminc = [sum(incidence[:i]) for i in range(len(incidence))]

        infc = site.thetahist

        section = rf"""
# {name}
## Incidence
```python
bar(list(range(len(cuminc))), cuminc)
xlabel('Time')
ylabel('Incidence')
title('Incidence per unit of time')
```
```python
bar(list(range(len(infc))), infc)
title('Number of infectious individuals arriving per unit of time')
xlabel('Time')
ylabel('Infectious individuous')
```  
        """
        return section


    def genEpi(self):
        """
        Generate epidemiological report.
        """
        epistats = self.sim.g.getEpistats()
        cumcities = [sum(epistats[1][:i]) for i in range(len(epistats[1]))]


        # print (epistats[0],average(epistats[1]),epistats[2],epistats[3],epistats[4],'sp')
        section = rf"""
# Epidemiological Statistics

## Network-wide Epidemiological Statistics
In the table  below, we present some useful epidemiological statistics about this simulation.
They include the following descriptors:

 - **Epidemic size (people)** This is the total number 
of cases that happened during the full course of the simulation.
 - **Epidemic size (sites)** This is the total number of sites infected durint the epidemic.
 - **Epidemic speed** This is the average number of new cities infected 
per unit of time, during the epidemic.
 - **Epidemic duration** The total number of units of time, the epidemic lasted.
- **Median survival time** The time it took for fifty percent of the cities to become infected.


 |---------------|---------------|
 | Size (people) | {epistats[0]} |
 |---------------|---------------|
 | Speed         | {mean(epistats[1])} |
 |---------------|---------------|
 | Size (sites)  | {epistats[2]} |
 |---------------|---------------|
 | Duration      | {epistats[3]} |
 |---------------|---------------|
 | Survival      | {epistats[4]} |
 |---------------|---------------|
 | Total vaccines| {epistats[5]} |
 |---------------|---------------|
 |Total Quarantined | {epistats[6]}|

```python
bar(list(range(len(cumcities))), cumcities)
ylabel('Number of infected cities')
xlabel('Time')
```
            """
        return section


    def Assemble(self, type, save=True):
        """
        Assemble the type of report desired
        types:
        0: None
        1: network only
        2: epidemiological only
        3: both
        """

        print("Starting report generation...")

        sitehead = r"""
# Site Specific Analyses

 - **Centrality:** Also known as closeness. A measure of global centrality, is the 
inverse of the sum of the shortest paths to all other nodes
in the graph.
 - **Degree:** The order (degree) of a node is the number of its attached links 
and is a simple, but effective measure of nodal importance. 

The higher its value, the more a node is important in a graph 
as many links converge to it. Hub nodes have a high order, 
while terminal points have an order that can be as low as 1. 

A perfect hub would have its order equal to the summation of 
all the orders of the other nodes in the graph and a perfect 
spoke would have an order of 1.

 - **Theta Index:** Measures the function of a node, that is the average
amount of traffic per intersection. The higher theta is,
the greater the load of the network.
 - **Betweeness:** Is the number of times any node figures in the the shortest path
between any other pair of nodes.
"""
        from time import time
        tail = r""
        if type == 1:
            start = time()
            latexsrc = header + self.genNetTitle() + self.graphDesc()
            # Generate reports for every site specified in the script, if any.
            if self.sim.siteRep:
                latexsrc += sitehead
                for site in self.sim.siteRep:
                    latexsrc += self.siteReport(site)
            latexsrc += tail
            timer = time() - start
            print('Time to generate Network report: %s seconds.' % timer)
            repname = 'net_report'
        elif type == 2:
            start = time()
            latexsrc = header + self.genEpiTitle() + self.genEpi()
            if self.sim.siteRep:
                for site in self.sim.siteRep:
                    latexsrc += self.genSiteEpi(site)
            latexsrc += tail
            timer = time() - start
            print('Time to generate Epidemiological report: %s seconds.' % timer)
            if self.sim.gui:
                self.sim.gui.textEdit1.insertParagraph('Time to generate epidemiological report: %s seconds.' % timer, -1)
            repname = 'epi_report'
        elif type == 3:
            start = time()
            latexsrc = header + self.genFullTitle() + self.graphDesc()
            # Generate reports for every site specified in the script, if any.
            if self.sim.siteRep:
                latexsrc += sitehead
                for site in self.sim.siteRep:
                    latexsrc += self.siteReport(site)
            latexsrc += self.genEpi()
            if self.sim.siteRep:
                for site in self.sim.siteRep:
                    latexsrc += self.genSiteEpi(site)
            latexsrc += tail
            timer = time() - start
            print('Time to generate full report: %s seconds.' % timer)
            repname = 'full_report'
        else:
            return
        if save:
            self.savenBuild(repname, latexsrc)
        return latexsrc


    def Say(self, string):
        """
        Exits outputs messages to the console or the gui accordingly
        """
        print(string)


    def savenBuild(self, name, src):
        """
        Saves the LaTeX in a newly created directory and builds it.
        """
        dirname = self.sim.modelName + r'-report-'
        Path = dirname + ctime()
        Path = Path.replace(' ', '-')
        os.system('mkdir ' + Path)
        os.chdir(Path)
        print(f'Saving {name}.pmd')
        with codecs.open(f'{name}.pmd', 'w', self.encoding) as fs:
            fs.write(src)

        pweave.weave(f"{name}.pmd", doctype='markdown')


