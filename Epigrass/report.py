"""
This module generates a report of the network simulation model
using LaTeX.
"""

import codecs
from time import ctime, time
import os
import re
import io
import sys
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import base64
import datetime

from pylab import *




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
        self.title_template = """
# Epigrass Report

Model {modname} Network Report
 
John Doe
 
{data}


### Abstract
Edit the report.md file and add your model's description here.

        """

    def genNetTitle(self):
        """
        Generates title section of the preamble from 
        data extracted from the simulation.
        """
        modname = self.sim.modelName
        title = self.title_template.format(modname=modname, data=datetime.date.today())

        return title

    def genEpiTitle(self):
        """
        Generates title section of the preamble from 
        data extracted from the simulation.
        """
        modname = self.sim.modelName
        title = self.title_template.format(modname=modname, data=datetime.date.today())

        return title

    def genFullTitle(self):
        """
        Generates title section of the preamble from 
        data extracted from the simulation.
        """
        modname = self.sim.modelName
        title = self.title_template.format(modname=modname, data=datetime.date.today())
        return title

    def gen_graph_desc(self):
        """
        Generates the Graph description section.
        """
        stats = tuple(self.sim.g.doStats())
        nodd = sum([1 for i in self.sim.g.site_list if len(i.neighbors) % 2 != 0])
        Trav = 'No'
        Eul = 'No'
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

Wiener's $D ={stats[2]}$

## Mean Distance
The mean distance of a network is the mean of of the set of shortest paths, 
excluding the 0-length paths.""" + \
                  r"""
                  $\bar{D}=""" + f'{stats[3]}$' + \
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
""" + \
r"""
$\iota=\frac{L(N)}{W(N)}=""" + f'{stats[7]}$' + \
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
""" + \
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
        context = {
            'stats': stats,
            'nnodes': nnodes,
            'nedges': nedges,
            'Eul': Eul,
            'Trav': Trav,
            'Ham': Ham
        }
        processed_section = self.execute_code_blocks(section, context)
        return processed_section

    def site_report(self, geoc):
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
$$B={stats[3]}$$\
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
        context = {
            'name': name,
            'cuminc': cuminc,
            'incidence': incidence,
            'totcases': totcases,
            'infc': infc
        }
        processed_section = self.execute_code_blocks(section, context)
        return processed_section

    def genEpi(self):
        """
        Generate epidemiological report.
        :Returns:
        section: The markdown text of the section
        context: A dictionary with variables to be used in the section
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

 | Metric | Value   |
 |---------------|---------------|
 | Size (people) | {epistats[0]} |
 | Speed         | {mean(epistats[1])} |
 | Size (sites)  | {epistats[2]} |
 | Duration      | {epistats[3]} |
 | Survival      | {epistats[4]} |
 | Total vaccines| {epistats[5]} |
 |Total Quarantined | {epistats[6]}|
  

```python
bar(list(range(len(cumcities))), cumcities)
ylabel('Number of infected cities')
xlabel('Time')
```
            """
        context = {'epistats': epistats,
                    'cumcities': cumcities
                   }
        processed_section = self.execute_code_blocks(section, context)
        return processed_section

    def Assemble(self, reporttype, save=True):
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

        tail = r""
        if reporttype == 1:
            start = time.time()
            markdownsrc = self.header + self.genNetTitle() + self.gen_graph_desc()
            # Generate reports for every site specified in the script, if any.
            if self.sim.siteRep:
                markdownsrc += sitehead
                for site in self.sim.siteRep:
                    markdownsrc += self.site_report(site)
            markdownsrc += tail
            timer = time.time() - start
            print('Time to generate Network report: %s seconds.' % timer)
            repname = 'net_report'
        elif reporttype == 2:
            start = time.time()
            markdownsrc = self.header + self.genEpiTitle() + self.genEpi()
            if self.sim.siteRep:
                for site in self.sim.siteRep:
                    sesrc = self.genSiteEpi(site)
                    markdownsrc += sesrc
            markdownsrc += tail
            timer = time.time() - start
            print('Time to generate Epidemiological report: %s seconds.' % timer)
            if self.sim.gui:
                self.sim.gui.textEdit1.insertParagraph('Time to generate epidemiological report: %s seconds.' % timer,
                                                       -1)
            repname = 'epi_report'
        elif reporttype == 3:
            start = time.time()
            gsrc = self.gen_graph_desc()
            markdownsrc = self.header + self.genFullTitle() + gsrc
            # Generate reports for every site specified in the script, if any.
            if self.sim.siteRep:
                markdownsrc += sitehead
                for site in self.sim.siteRep:
                    markdownsrc += self.site_report(site)
            markdownsrc += self.genEpi()
            if self.sim.siteRep:
                for site in self.sim.siteRep:
                    markdownsrc += self.genSiteEpi(site)
            markdownsrc += tail
            timer = time.time() - start
            print('Time to generate full report: %s seconds.' % timer)
            repname = 'full_report'
        else:
            return
        if save:
            self.savenBuild(repname, markdownsrc)
        return markdownsrc

    def Say(self, string):
        """
        Exits outputs messages to the console or the gui accordingly
        """
        print(string)

    def execute_code_blocks(self, markdown_content, context={}):
        """
        Execute Python code blocks in markdown and replace them with their output.
        """
        # Pattern to match ```python code blocks
        code_block_pattern = r'```python\n(.*?)\n```'
        
        def execute_and_replace(match):
            code = match.group(1)
            
            # Create a string buffer to capture output
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            
            try:
                # Redirect stdout and stderr
                sys.stdout = stdout_buffer
                sys.stderr = stderr_buffer
                
                # Create execution context with simulation data
                exec_globals = {
                    'self': self,
                    'sim': self.sim,
                    'plt': plt,
                    'figure': plt.figure,
                    'plot': plt.plot,
                    'bar': plt.bar,
                    'hist': plt.hist,
                    'xlabel': plt.xlabel,
                    'ylabel': plt.ylabel,
                    'title': plt.title,
                    'colorbar': plt.colorbar,
                    'pcolor': plt.pcolor,
                    'show': plt.show,
                    'savefig': plt.savefig,
                    'mean': lambda x: sum(x) / len(x) if len(x) > 0 else 0,
                    'sum': sum,
                    'len': len,
                    'range': range,
                    'list': list,
                }
                exec_globals.update(context)
                # Execute the code
                exec(code, exec_globals)
                
                # Get any text output
                output = stdout_buffer.getvalue()
                error_output = stderr_buffer.getvalue()
                
                # Check if a plot was created
                fig = plt.gcf()
                plot_output = ""
                
                if fig.get_axes():  # If there are axes, a plot was created
                    # Save plot to base64 string
                    img_buffer = io.BytesIO()
                    fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
                    img_buffer.seek(0)
                    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                    plot_output = f"\n![Plot](data:image/png;base64,{img_base64})\n"
                    plt.close(fig)  # Close the figure to free memory
                
                # Combine text output and plot
                result = ""
                if output.strip():
                    result += f"```\n{output.strip()}\n```\n"
                if error_output.strip():
                    result += f"```\nError: {error_output.strip()}\n```\n"
                result += plot_output
                
                return result if result.strip() else "```\n# Code executed successfully\n```"
                
            except Exception as e:
                return f"```\nError executing code: {str(e)}\n```"
            
            finally:
                # Restore stdout and stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr
        
        # Replace all code blocks with their executed results
        processed_content = re.sub(code_block_pattern, execute_and_replace, markdown_content, flags=re.DOTALL)
        
        return processed_content

    def savenBuild(self, name, src):
        """
        Saves the report in markdown format in a new directory.
        Executes Python code blocks and replaces them with their output.
        """
        dirname = self.sim.modelName + '-report-'
        path = dirname + ctime().replace(' ', '-')
        os.makedirs(path, exist_ok=True)
        os.chdir(path)
        
        # Execute code blocks and replace them with results
        print("Executing code blocks in markdown...")
        processed_src = self.execute_code_blocks(src)
        
        md_file = f"{name}.md"
        print(f'Saving {md_file}')
        with codecs.open(md_file, 'w', self.encoding) as f:
            f.write(processed_src)
        print(f'Successfully generated markdown report at: {os.path.join(path, md_file)}')
