"""
This module generates a report of the network simulation model
using LaTeX.
"""
from __future__ import absolute_import
from __future__ import print_function
import os, sys, commands, string, time, matplotlib, codecs
from six.moves import range
#matplotlib.use("Agg")

#from pylab import *
#from matplotlib.mlab import *

header =r"""
\documentclass[a4paper,10pt]{report}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage[utf8]{inputenc}
"""

class report:
    """
    Generates reports in pdf format.
    Takes as input arg. a simulation object.
    """
    def __init__(self, simulation):
        self.workdir = os.getcwd()
        pltx = commands.getoutput('which latex')
        pppdfltx = commands.getoutput('which pdflatex')
        if pltx.startswith('which:'):
            self.latex = 0
        else:
            self.latex = 1
        if pppdfltx.startswith('which:'):
            self.pdflatex = 0
        else:
            self.pdflatex = 1
        if not (self.latex or self.pdflatex):

            sys.exit('Cannot Generate report. LaTeX not present.')
        self.sim = simulation
        self.encoding = self.sim.encoding
        if self.encoding == 'latin-1':enc = 'latin1'
        elif self.encoding == 'utf-8':enc = 'utf8'
        self.header =r"""
        \documentclass[a4paper,10pt]{report}
        \usepackage{amsmath}
        \usepackage{amsfonts}
        \usepackage{amssymb}
        \usepackage{graphicx}
        \usepackage[%s]{inputenc}
        """%enc

    
    def genNetTitle(self):
        """
        Generates title section of the preamble from 
        data extracted from the simulation.
        """
        modname = self.sim.modelName
        title = r"""
        \title{Model %s Network Report}
        \author{John Doe}
        \begin{document}
        \maketitle
        \tableofcontents
        \listoffigures
        \begin{abstract}
        Edit the report.tex file and add your model's description here.
        \end{abstract}
        """% modname.split('/')[-1]
        
        return title
        
    def genEpiTitle(self):
        """
        Generates title section of the preamble from 
        data extracted from the simulation.
        """
        modname = self.sim.modelName
        title = r"""
        \title{Model %s Epidemiological Report}
        \author{John Doe}
        \begin{document}
        \maketitle
        \tableofcontents
        \listoffigures
        \begin{abstract}
        Edit the report.tex file and add your model's description here.
        \end{abstract}
        """% modname.split('/')[-1]
        
        return title
        
    def genFullTitle(self):
        """
        Generates title section of the preamble from 
        data extracted from the simulation.
        """
        modname = self.sim.modelName
        title = r"""
        \title{Model %s Full Report}
        \author{John Doe}
        \begin{document}
        \maketitle
        \tableofcontents
        \listoffigures
        \begin{abstract}
        Edit the report.tex file and add your model's description here.
        \end{abstract}
        """% modname.split('/')[-1]
        
        return title
        
    def graphDesc(self):
        """
        Generates the Graph description section.
        """
        self.sim.g.drawGraph() # draws the network and saves to a file
        self.sim.g.plotDegreeDist() # draws the network and saves to a file
        stats = tuple(self.sim.g.doStats())
        nodd = sum([1 for i in self.sim.g.site_list if len(i.neighbors)%2 != 0])
        if nodd: #check if Graph is Eulerian and/or traversable
            Eul = 'No'
            if nodd == 2:
                Trav = 'Yes'
            else: Trav = 'No'
        else: Eul = 'Yes'
##        #formats distance matrix for LaTeX=========
##        m =''
##        for i in stats[0]:
##            l=''
##            for j in i:
##                l += '%s&' % j
##            l = l[:-1]+r'\\'
##            m += l
##        #print m, stats[0]
##        #======================================
##        cols = stats[0].shape[1]
        nnodes = len(self.sim.g.site_list)
        nedges = len(self.sim.g.edge_list)
        deglist = [len(i.neighbors) for i in self.sim.g.site_list]
        #check if graph is hamiltonian
        if nnodes >= 3:
            if min(deglist) >= nnodes/2.:
                Ham = 'Yes'
            else: Ham = 'Possibly'
        else: Ham = 'Yes'
        
        hist(stats[0].flat,normed=1)
        title('Shortest paths distribution')
        #colorbar()
        savefig('spd.png')
        close()
        pcolor(stats[12])
        #yticks(())
        #xticks(())
        title('Adjacency Matrix')
        colorbar()
        savefig('am.png')
        close()
        
        matrix = r"""
        \chapter{General Network Analyses}
        Figure \ref{fig:g} contains a simple drawing of your graph. If your network 
        is not very complex,it can help you to verify if the topology specifed correspond to
        your expectations.
        \begin{figure}[h]
        \includegraphics[width=8cm]{graph.png}
        \caption{Network diagram}
        \label{fig:g}
        \end{figure}
        \section{Network Descriptive Statistics}
        In this section you will find quantitative descriptors and plots 
        that will help you analyze you network.
        
        \subsection{Basic Numbers}
        \begin{description}
        \item[Order (Number of Nodes):] %s
        \item[Size (Number of Edges):] %s
        \item[Eulerian:] %s
        \item[Traversable:] %s
        \item[Hamiltonian:] %s
        \end{description}
        \begin{figure}[h]
        \includegraphics[width=8cm]{degdist.png}
        \caption{Distribution of nodes degrees}
        \label{fig:dd}
        \end{figure}
        
        \subsection{Distance matrix}
        The distance Matrix (figure \ref{fig:spd}) represents the number of edges separating any
        pair of nodes via the shortest path between them. \footnote{Due to size restriction, 
        the matrix is not included in this report but it can be found in the database 
        table containing the results of your simulation.}
        \begin{figure}[h]
        \includegraphics[width=8cm]{spd.png}
        \caption{Shortest paths distribution}
        \label{fig:spd}
        \end{figure}
        
        \subsection{Adjacencyy Matrix}
        The most basic measure of accessibility involves network connectivity
        where a network is represented as a connectivity matrix(figure \ref{fig:cm}), which 
        expresses the connectivity of each node with its adjacent nodes. 
        
        The number of columns and rows in this matrix is equal to the number 
        of nodes in the network and a value of 1 is given for each cell where 
        this is a connected pair and a value of 0 for each cell where there 
        is an unconnected pair. The summation of this matrix provides a very 
        basic measure of accessibility, also known as the degree of a node.
        \begin{figure}[h]
        \includegraphics[width=8cm]{am.png}
        \caption{Connectivity matrix}
        \label{fig:cm}
        \end{figure}
        
        """ % (nnodes,nedges,Eul,Trav, Ham)
        indices = r"""
        \subsection{Number of Cycles}
        The maximum number of independent cycles in a graph.
        This number ($u$) is estimated by knowing the number of nodes ($v$), 
        links ($e$) and of sub-graphs ($p$); $u = e-v+p$.
        
        Trees and simple networks will have a value of 0 since they have 
        no cycles. 
        The more complex a network is, the higher the value of u, 
        so it can be used as an indicator of the level of development 
        of a transport system.
        
        Cycles(u) $=%s$
        
        \subsection{Wiener Distance}
        The Wiener distance is the sum of all the shortest distances in the network.
        
        Wiener's D $=%s$
        
        \subsection{Mean Distance}
        The mean distance of a network is the mean of of the set of shortest paths, 
        excluding the 0-length paths.
        
        $\bar{D}=%s$ 
        \subsection{Network Diameter}
        The diameter of a network is the longest element of the shortest paths set.
        
        $D(N)=%s$
        \subsection{Length of the Network}
        The length of a network is the sum in metric units (e.g., km) of all the edges in the network.
        
        $L(N)=%s$
        \subsection{Weight of the Network}
        The weight of a network is the weight of all nodes in the graph ($W(N)$), which is the summation 
        of each node's order ($o$) multiplied by 2 for all orders above 1.
        
        $W(N)=%s$
        \subsection{Iota ($\iota$) Index}
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
        
        $\iota=\dfrac{L(N)}{W(N)}=%s$
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
        
        $\Pi=L(N)/D(d)=%s$
        \subsection{Beta ($\beta$) Index}
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
        
        $\beta = %s$    
        
        """% stats[1:10]
        section = matrix+indices
        return section
    def siteReport(self,geoc):
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
        site.plotItself()
        section = r"""
        \section{%s}
        \subsection{Centrality}
        $$C=%s$$
        \subsection{Degree}
        $$D=%s$$
        \subsection{Theta Index}
        $$\theta=%s$$
        \subsection{Betweeness}
        $$B=%s$$
        \begin{figure}[h]
        \centering
        \includegraphics[width=8cm]{%s.png}
        \caption{Time series plot}
        \end{figure}
        """ % tuple(name+stats+[geoc])
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
        cuminc=[sum(incidence[:i]) for i in range(len(incidence))]
        
        infc = site.thetahist
        bar(list(range(len(cuminc))),cuminc)
        xlabel('Time')
        ylabel('Incidence')
        savefig('inc.png')
        close()
        bar(list(range(len(infc))),infc)
        xlabel('Time')
        ylabel('Infectious individuous')
        savefig('inf.png')
        close()
        section = r"""
        \section{%s}
        \subsection{Incidence}
        \begin{figure}[h]
        \centering
        \includegraphics[width=8cm]{%s.png}
        \caption{Incidence per unit of time}
        \end{figure}
        \subsection{Total number of cases}
        $$N_c=%s$$
        \subsection{Infectious arriving}
        \begin{figure}[h]
        \centering
        \includegraphics[width=8cm]{%s.png}
        \caption{Number of infectious individuals arriving per unit of time}
        \end{figure}
        """%(name,'inc',totcases,'inf')
        return section
    def genEpi(self):
        """
        Generate epidemiological report.
        """
        epistats = self.sim.g.getEpistats()
        cumcities = [sum(epistats[1][:i]) for i in range(len(epistats[1]))]
        bar(list(range(len(cumcities))),cumcities)
        ylabel=('Number of infected cities')
        xlabel=('Time')
        savefig('sp.png')
        close()
        #print (epistats[0],average(epistats[1]),epistats[2],epistats[3],epistats[4],'sp')
        section = r"""
        \chapter{Epidemiological Statistics}
        \section{Network-wide Epidemiological Statistics}
        In the table \ref{tab:epi} below, we presen some useful epidemiological statistics about this simulation.
        They include the following descriptors:
        \begin{description}
        \item [Epidemic size (people)] This is the total number 
        of cases that happened during the full course of the simulation.
        \item [Epidemic size (sites)] This is the total number of sites infected durint the epidemic.
        \item [Epidemic speed] This is the average number of new cities infected 
        per unit of time, during the epidemic.
        \item [Epidemic duration] The total number of units of time, the epidemic lasted.
        \item [Median survival time] The time it took for fifty percent of the cities to become infected.
        \end{description}
        \begin{table}
        \caption{Epidemic statistics}
        \centering
        \begin{tabular}{|c|c|}
        \hline
         Size (people) & %s \\ \hline 
         Speed & %s \\ \hline
         Size (sites)& %s \\ \hline 
         Duration & %s \\ \hline
         Survival & %s \\ \hline
         Total vaccines & %s \\ \hline
         Total Quarantined & %s \\ \hline
        \end{tabular} 
        \label{tab:epi}
        \end{table}
        \begin{figure}[h]
        \centering
        \includegraphics[width=8cm]{%s.png}
        \caption{Speed of the epidemic spread over time}
        \end{figure}
        """%(epistats[0],mean(epistats[1]),epistats[2],epistats[3],
        epistats[4],epistats[5],epistats[6],'sp')
        return section
    
    def Assemble(self,type):
        """
        Assemble the type of report desired
        types:
        1: network only
        2: epidemiological only
        3: both
        """
        dirname = self.sim.modelName+ r'-report-'
        Path= dirname+time.ctime()
        Path = Path.replace(' ','-')
        os.system('mkdir '+Path)
        os.chdir(Path)
        print("Starting report generation...")
        
        sitehead = r"""
                \chapter{Site Specific Analyses}"
                \begin{description}
                \item[Centrality:]Also known as closeness. A measure of global centrality, is the 
                inverse of the sum of the shortest paths to all other nodes
                in the graph.
                \item[Degree:]The order (degree) of a node is the number of its attached links 
                and is a simple, but effective measure of nodal importance. 
                
                The higher its value, the more a node is important in a graph 
                as many links converge to it. Hub nodes have a high order, 
                while terminal points have an order that can be as low as 1. 
                
                A perfect hub would have its order equal to the summation of 
                all the orders of the other nodes in the graph and a perfect 
                spoke would have an order of 1.
                \item[Theta Index:]Measures the function of a node, that is the average
                amount of traffic per intersection. The higher theta is,
                the greater the load of the network.
                \item[Betweeness:]Is the number of times any node figures in the the shortest path
                between any other pair of nodes.
                \end{description}
                """
        if type == 1:
            
            start = time.clock()
            tail =r"\end{document}"
            latexsrc = header + self.genNetTitle() + self.graphDesc() 
            # Generate reports for every site specified in the script, if any.
            if self.sim.siteRep:
                latexsrc += sitehead
                for site in self.sim.siteRep:
                    latexsrc += self.siteReport(site)
            latexsrc += tail
            timer = time.clock()-start
            print('Time to generate Network report: %s seconds.'% timer)
            if self.sim.gui:
                self.sim.gui.textEdit1.insertParagraph('Time to generate Network report: %s seconds.'% timer,-1)
            self.savenBuild('Netreport',latexsrc)
        elif type == 2:
            start = time.clock()
            tail =r"\end{document}"
            latexsrc = header + self.genEpiTitle() + self.genEpi()
            if self.sim.siteRep:
                for site in self.sim.siteRep:
                    latexsrc += self.genSiteEpi(site)
            latexsrc +=  tail
            timer = time.clock()-start
            print('Time to generate Epidemiological report: %s seconds.'% timer)
            if self.sim.gui:
                self.sim.gui.textEdit1.insertParagraph('Time to generate epidemiological report: %s seconds.'% timer,-1)
            self.savenBuild('epireport',latexsrc)
        elif type == 3:
            start = time.clock()
            tail =r"\end{document}"
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
            timer = time.clock()-start
            print('Time to generate full report: %s seconds.'% timer)
            if self.sim.gui:
                self.sim.gui.textEdit1.insertParagraph('Time to generate full report: %s seconds.'% timer,-1)
            self.savenBuild('fullreport',latexsrc)
    
    def Say(self,string):
        """
        Exits outputs messages to the console or the gui accordingly 
        """
        if self.sim.gui:
            self.sim.gui.textEdit1.insertParagraph(string,-1)
        else:
            print(string)
    
    def savenBuild(self,name,src):
        """
        Saves the LaTeX in a newly created directory and builds it.
        """
        fs = codecs.open(name+'.tex','w', self.encoding)
        fs.write(src)
        fs.close()
        
        
        if self.pdflatex:
            os.system('pdflatex --interaction nonstopmode %s.tex'%name)
            os.system('pdflatex --interaction nonstopmode %s.tex'%name)
            self.Say('PDF compiled!')
            self.sim.repname = os.getcwd()+'/'+name+'.pdf'
            os.chdir(self.workdir)
            #do it twice to get the references right
        elif self.latex:
            os.system('latex %s.tex'%name)
            os.system('latex %s.tex'%name)
            self.Say('DVI compiled!')
            self.sim.repname = os.getcwd()+'/'+name+'.dvi'
            os.chdir(self.workdir)
        else:
            self.Say("""You don't seem to have 'latex' or 'pdflatex' instaled.
                The tex source for the report, has been generated
                and can be compiled later, when these tools are available.""")


            
