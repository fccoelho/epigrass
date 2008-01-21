""" 
This Module contains the definitions of objects for spatial simulation on geo reference spaces.
"""
import sys, matplotlib
matplotlib.use("Agg")
from pylab import *
#import dgraph
from numpy import *
from numpy.random import *
from types import MethodType
from Epigrass.data_io import *


class siteobj:
    """
    Basic site object containing attributes and methods common to all
    site objects.
    """
    def __init__(self, name, initpop,coords,geocode,values=()):
        """
        Set initial values for site attributes.
        
        -name: name of the locality
        
        -coords: site coordinates.
        
        -initpop: total population size.
        
        -geocode: integer id code for site
        
        -values: Tuple containing adicional values from the sites file
        """
        self.id = self #reference to site instance
        self.stochtransp = 1 #Flag for stochastic transportation
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
        self.thetahist = [] #infected arriving per time step
        self.passlist = []
        self.totalcases = 0
        self.vaccination = [[],[]] #time and coverage of vaccination event
        self.vaccineNow = 0 #flag to indicate that it is vaccination day
        self.vaccov = 0 #current vaccination coverage
        self.nVaccinated = 0
        self.quarantine = [sys.maxint,0]
        self.nQuarantined = 0
        self.geocode = geocode
        self.painted = 0 # Flag for the graph display
        self.modtype = None
        self.migInf = [] #infectious individuals able to migrate (time series)
        

    def createModel(self,init,modtype='SEIR',name='model1',v=[],bi=None,bp=None):
        """
        Creates a model of type modtype and defines its initial parameters.
        init -- initial conditions for the state variables tuple with fractions of the total 
        population in each category (state variable).
        par -- initial values for the parameters.
        v -- List of extra variables passed in the sites files
        bi, bp -- dictionaries containing all the inits and parms defined in the .epg model
        """
        Init = init
        N = self.totpop
        self.modtype = modtype
        self.values = v
        self.bi = bi
        self.bp = bp
        self.ts.append(list(array(Init,float)))
        self.model = popmodels(self.id,type=modtype,v=self.values,bi = self.bi, bp = self.bp)
        

    def runModel(self):
        """
        Iterate the model
        """
        if self.parentGraph.simstep in self.vaccination[0]:
            self.vaccineNow = 1
            self.vaccov = float(self.vaccination[1][self.vaccination[0].index(self.parentGraph.simstep)])
        if self.thetalist:
            theta = sum([i[1] for i in self.thetalist])
            self.infector = dict([i for i in self.thetalist if i[1] > 0]) #Only those that contribute at least one infected individual
        else:
            theta = 0
            self.infector = {}
        
      
        npass = sum(self.passlist)
        self.thetahist.append(theta) #keep a record of infected passenger arriving
        self.ts.append(self.model.step(self.ts[-1],theta,npass))
        self.thetalist = []   # reset self.thetalist (for the new timestep)
##        if self.parentGraph.gr: #updatn.box.length =es the visual graph display.
##            i = self.parentGraph.site_list.index(self)
##            if self.infected:
##                self.parentGraph.gr.nodes[i].box.length = self.parentGraph.gr.nodes[i].box.width =self.parentGraph.gr.nodes[i].box.height = (self.ts[-1][1]/float(self.totpop)+0.4)**1/3.
##                if not self.painted:
##                    self.parentGraph.lightGRNode(self,'r') 
        

    def vaccinate(self,cov):
        """
        At time t the population will be vaccinated with coverage cov.
        """
        
        self.nVaccinated = self.ts[-1][2]*cov
        self.ts[-1][2] = self.ts[-1][2]*(1-cov)
        
    def intervention(self,par,cov,efic):
        """
        From time t on, parameter par is changed to
        par * (1-cov*efic)
        """
        self.bp[par] = self.bp[par]*(1-cov*efic)
    
    def getTheta(self,npass, delay):
        """
        Returns the number of infected individuals in this 
        site commuting through the edge that called
        this function. 
        
        npass -- number of individuals leaving the node.
        """
        if delay>=len(self.migInf):
            delay = len(self.migInf)-1
        lag = -1- delay
        
        
        if not self.stochtransp:
            theta = npass * self.migInf[lag]/float(self.totpop) # infectious migrants
            
        else: #Stochastic migration
            #print lag, self.migInf
            #print npass
            try:
                theta = binomial(int(npass),self.migInf[lag]/float(self.totpop))
            except ValueError: #if npass is less than one
                theta = 0
        # Check if site is quarantined
        if self.parentGraph.simstep > self.quarantine[0]:
            self.nQuarantined = npass*self.quarantine[1]
            return theta*(1-self.quarantine[1]),npass*(1-self.quarantine[1])
        else:
            return theta,npass
    
    def getThetaindex(self):
        """
        Returns the Theta index.
        Measures the function of a node, that is the average
        amount of traffic per intersection. The higher theta is,
        the greater the load of the network.
        """
        if self.thidx:
            return self.thidx
        self.thidx = thidx = sum([(i.fmig+i.bmig)/2. for i in self.edges])/len(self.parentGraph.site_list)
        return thidx
    
    def receiveTheta(self,thetai, npass, sname):
        """
        Number of infectious individuals arriving from site i
        """
        self.thetalist.append((sname,thetai))
        self.passlist.append(npass)
    
    def plotItself(self):
        """
        plot site timeseries
        """
        a = transpose(array(self.ts))
        #figure(int(self.totpop))
        figure()
        for i in xrange(3):
            plot(transpose(a[i]))
        title(self.sitename)
        legend(('E','I','S'))
        xlabel('time(days)')
        savefig(str(self.geocode)+'.png')
        close()
        #show()
    
    def isNode(self):
        """
        find is given site is a node of a graph
        """
        if self.parentGraph:
            return 1
        else:
            return 0
    
    def getNeighbors(self):
        """
        Returns a dictionary of neighbooring sites as keys,
        and distances as values.
        """
        if not self.isNode():
            return []
        if self.neighbors:
            return self.neighbors
        
        n=[[i.source,i.dest,i.length] for i in self.edges]
        neigh = {}
        for i in n:
            #print len(i[0]),i[0][0].sitename,self.sitename
            #if len(i[0])==1: print self.edges[j].sites,self.edges[j].source.sitename,self.edges[j].dest.sitename
            idx = i.index(self)
            m = i.pop(idx)
            k = i[0]
            neigh[k] = i[-1]
            
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
                sys.exit('%s is not a neighbor of %s!'%(nei[0].sitename, self.sitename))
        else:
            if neighbor in self.neighbors:
                d = [e.length for e in self.edges if neighbor in e.sites][0]
                if d == 0:
                    print 'problem determining distance from neighboor'
            else:
                sys.exit('%s is not a neighbor of %s!'%(neighbor.sitename, self.sitename))
        
        return d
        
    def getDegree(self):
        """
        Returns the degrees of this site if it is part of a graph.
        The order (degree) of a node is the number of its attached links 
        and is a simple, but effective measure of nodal importance. 
        
        The higher its value, the more a node is important in a graph 
        as many links converge to it. Hub nodes have a high order, 
        while terminal points have an order that can be as low as 1. 
        
        A perfect hub would have its order equal to the summation of 
        all the orders of the other nodes in the graph and a perfect 
        spoke would have an order of 1.
        """
        if not self.isNode():
            return 0
        else:
            return len(self.edges)
            
    def doStats(self):
        """
        Calculate indices describing the node and return them in a list.
        """
        self.centrality = self.getCentrality()
        self.degree = self.getDegree()
        self.thidx = self.getThetaindex()
        self.betweeness = self.getBetweeness()
        
        return [self.centrality,self.degree,self.thidx, self.betweeness]
    
    def getCentrality(self):
        """
        Also known as closeness. A measure of global centrality, is the 
        inverse of the sum of the shortest paths to all other nodes
        in the graph.
        """
        #get position in the distance matrix.
        if self.centrality:
            return self.centrality
        pos = self.parentGraph.site_list.index(self)
        if not self.parentGraph.allPairs.any():
            self.parentGraph.getAllPairs()
        c = 1./sum(self.parentGraph.allPairs[pos])
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
                    B +=1
        return B
        

class popmodels:
    """
    Defines a library of discrete time population models
    """
    def __init__(self,parentsite,type='SIR',v=[],bi=None,bp=None):
        """
        defines which models a given site will use
        and set variable names accordingly.
        """
        self.type = type
        self.values = v
        self.bi = bi # dictionary of inits
        self.bp = bp # dictionary of parms
        self.parentSite = parentsite
        self.parentSite.vnames = ('E','I','S')
        self.selectModel(self.type)#sets self.step
        

        #print self.step
        
    def selectModel(self,type):
        """
        sets the model engine
        """
        
        if type=='SIR':
            self.step=self.stepSIR
        elif type == 'SIR_s':
            self.step=self.stepSIR_s
        elif type == 'SIS':
            self.step=self.stepSIS
        elif type == 'SIS_s':
            self.step=self.stepSIS_s
        elif type == 'SEIS':
            self.step=self.stepSEIS
        elif type == 'SEIS_s':
            self.step=self.stepSEIS_s
        elif type=='SEIR':
            self.step=self.stepSEIR
        elif type == 'SEIR_s':
            self.step = self.stepSEIR_s
        elif type == 'SIpRpS':
            self.step=self.stepSIpRpS
        elif type == 'SIpRpS_s':
            self.step=self.stepSIpRpS_s
        elif type == 'SEIpRpS':
            self.step=self.stepSEIpRpS
        elif type == 'SEIpRpS_s':
            self.step=self.stepSEIpRpS_s
        elif type == 'SIpR':
            self.parentSite.incidence2 = []
            self.step=self.stepSIpR
        elif type == 'SIpR_s':
            self.parentSite.incidence2 = []
            self.step=self.stepSIpR_s
        elif type == 'SEIpR':
            self.parentSite.incidence2 = []
            self.step=self.stepSEIpR
        elif type == 'SEIpR_s':
            self.parentSite.incidence2 = []
            self.step=self.stepSEIpR_s
        elif type == 'SIRS':
            self.step=self.stepSIRS
        elif type == 'SIRS_s':
            self.step=self.stepSIRS_s
        elif type == 'Influenza':
            self.step = self.stepFlu
        elif type == 'multiple':
            self.step = self.multipleStep
        elif type == 'Custom':
            #adds the user model as a method of instance self
            try:
                #TODO: move this import to the graph level
                import CustomModel
                self.step = MethodType(CustomModel.Model,self)
            except ImportError:
                print "You have to Create a CustomModel.py file before you can select\nthe Custom model type"
        else:
            sys.exit('Model type specified in .epg file is invalid')
            
    
    def multipleStep(self,inits,par,theta=0, npass=0, modelos=[]):
        """
        Run multiple models on a single site
        - Inits and par are a list of lists.
        - modelos is a list of of the modeltypes.
        """
        if not modelos:
            raise Error, 'You have to define a list of model types when using "multiple"'
        if not isinstance(inits[0],list):
            raise Error, 'Model type is "multiple" but inits is not a tuple'
        if not isinstance(par[0],list):
            raise Error, 'Model type is "multiple" but par is not a tuple'
            
        results=[]
        for i,m in enumerate(modelos):
            results.append(selectModel(m)(inits[i],par[i],theta,npass))
        return results
        
    
    def stepFlu(self,vars,N, theta=0,npass=0):
        """
        Flu model with classes S,E,I subclinical, I mild, I medium, I serious, deaths
        """
        #Variable long names to be used in the database output.
        self.parentSite.vnames = ('Susc_age1','Incub_age1','Subc_age1','Sympt_age1','Comp_age1',
        'Susc_age2','Incub_age2','Subc_age2','Sympt_age2','Comp_age2',
        'Susc_age3','Incub_age3','Subc_age3','Sympt_age3','Comp_age3',
        'Susc_age4','Incub_age4','Subc_age4','Sympt_age4','Comp_age4',)
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            S1,E1,Is1,Ic1,Ig1 = (self.bi['s1'],self.bi['e1'],self.bi['is1'],self.bi['ic1'],self.bi['ig1'])
            S2,E2,Is2,Ic2,Ig2 = (self.bi['s2'],self.bi['e2'],self.bi['is2'],self.bi['ic2'],self.bi['ig2'])
            S3,E3,Is3,Ic3,Ig3 = (self.bi['s3'],self.bi['e3'],self.bi['is3'],self.bi['ic3'],self.bi['ig3'])
            S4,E4,Is4,Ic4,Ig4 = (self.bi['s4'],self.bi['e4'],self.bi['is4'],self.bi['ic4'],self.bi['ig4'])
        else: #get values from last time step
            S1,E1,Is1,Ic1,Ig1,S2,E2,Is2,Ic2,Ig2,S3,E3,Is3,Ic3,Ig3,S4,E4,Is4,Ic4,Ig4 = vars
        N = self.parentSite.totpop
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        #parameters: alpha,beta,r,e,c,g,d,pc1,pc2,pc3,pc4,pp1,pp2,pp3,pp4,b 
        
        #Vacination event 
        if self.parentSite.vaccineNow:
            S1 -= self.parentSite.vaccov*S1
            S2 -= self.parentSite.vaccov*S2
            S3 -= self.parentSite.vaccov*S3
            S4 -= self.parentSite.vaccov*S4
        
        #New cases by age class
        #beta=eval(self.values[2])
        
        Infectantes = Ig1+Ig2+Ig3+Ig4+Ic1+Ic2+Ic3+Ic4+0.5*(Is1+Is2+Is3+Is4)+theta
        L1pos = float(beta)*S1*(Infectantes/(N+npass))**alpha
        L2pos = float(beta)*S2*(Infectantes/(N+npass))**alpha
        L3pos = float(beta)*S3*(Infectantes/(N+npass))**alpha
        L4pos = float(beta)*S4*(Infectantes/(N+npass))**alpha
        
        ######################
        Lpos = L1pos+L2pos+L3pos+L4pos
        self.parentSite.totalcases+=Lpos
        # Model
        # 0-2 anos
        E1pos = L1pos + (1-e)*E1
        Is1pos = (1-(pc1*c+(1-pc1)*r))*Is1 + e*E1
        Ic1pos = (1-(pp1*g+(1-pp1)*r))*Ic1 + pc1*c*Is1
        Ig1pos = (1-d)*Ig1 + pp1*g*Ic1
        S1pos = b+S1 - L1pos
        # 3-14 anos
        E2pos = L2pos + (1-e)*E2
        Is2pos = (1-(pc2*c+(1-pc2)*r))*Is2 + e*E2
        Ic2pos = (1-(pp2*g+(1-pp2)*r))*Ic2 + pc2*c*Is2
        Ig2pos = (1-d)*Ig2 + pp2*g*Ic2
        S2pos = b+S2 - L2pos
        # 15-59 anos
        E3pos = L3pos + (1-e)*E3
        Is3pos = (1-(pc3*c+(1-pc3)*r))*Is3 + e*E3
        Ic3pos = (1-(pp3*g+(1-pp3)*r))*Ic3 + pc3*c*Is3
        Ig3pos = (1-d)*Ig3 + pp3*g*Ic3
        S3pos = b+S3 - L3pos
        # >60 anos
        E4pos = L4pos + (1-e)*E4
        Is4pos = (1-(pc4*c+(1-pc4)*r))*Is4 + e*E4
        Ic4pos = (1-(pp4*g+(1-pp4)*r))*Ic4 + pc4*c*Is4
        Ig4pos = (1-d)*Ig4 + pp4*g*Ic4
        S4pos = b+S4 - L4pos
        # Updating stats
        
        self.parentSite.incidence.append(Lpos)
        # Raises site infected flag and adds parent site to the epidemic history list.
        if not self.parentSite.infected: 
            if Lpos > 0:
                #if not self.parentSite.infected:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ig1pos+Ig2pos+Ig3pos+Ig4pos+Ic1pos+Ic2pos+Ic3pos+Ic4pos+0.5*(Is1pos+Is2pos+Is3pos+Is4pos))
        # Return variable values
        return [S1pos,E1pos,Is1pos,Ic1pos,Ig1pos,S2pos,E2pos,Is2pos,
        Ic2pos,Ig2pos,S3pos,E3pos,Is3pos,Ic3pos,Ig3pos,S4pos,
        E4pos,Is4pos,Ic4pos,Ig4pos]
        
        
    def stepSIS(self,inits,theta=0, npass=0):
        """
        calculates the model SIS, and return its values (no demographics)
        - inits = (E,I,S)
        - theta = infectious individuals from neighbor sites
        """
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else:
            E,I,S = inits
        N = self.parentSite.totpop
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        #parameter: beta,alpha,e,r,delta,b,w,p
        Lpos = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
        self.parentSite.totalcases += Lpos #update number of cases
        # Model
        Ipos = (1-r)*I + Lpos
        Spos = S + b - Lpos + r*I
        # Updating stats
        self.parentSite.incidence.append(Lpos)
        # Raises site infected flag and adds parent site to the epidemic history list.
        if not self.parentSite.infected: 
            if Lpos > 0:
                #if not self.parentSite.infected:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ipos)
        return [0,Ipos,Spos]
        
    def stepSIS_s(self,inits=(0,0,0),theta=0, npass=0,dist='poisson'):
        """
        Defines an stochastic model SIS:
        - inits = (E,I,S)
        - theta = infectious individuals from neighbor sites
        """
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else:
            E,I,S = inits
        N = self.parentSite.totpop
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        # parameter: beta,alpha,e,r,delta,b,w,p
        Lpos_esp = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
        
        if dist == 'poisson':
            Lpos = poisson(Lpos_esp)
        elif dist == 'negbin':
            prob = I/(I+Lpos_esp) #convertin between parameterizations
            Lpos = negative_binomial(I,prob)
        self.parentSite.totalcases += Lpos #update number of cases   
        # Model
        Ipos = (1-r)*I + Lpos
        Spos = S + b - Lpos + r*I
        # Updating stats
        self.parentSite.incidence.append(Lpos)
        if not self.parentSite.infected:
            if Lpos > 0:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ipos)
        
        return [0,Ipos,Spos]
    
    def stepSIR(self,inits,theta=0, npass=0):
        """
        calculates the model SIR, and return its values (no demographics)
        - inits = (E,I,S)
        - theta = infectious individuals from neighbor sites
        """
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else:
            E,I,S = inits
        N = self.parentSite.totpop
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        # parameter: beta,alpha,e,r,delta,b,w,p
        Lpos = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
        self.parentSite.totalcases += Lpos #update number of cases
        # Model
        Ipos = (1-r)*I + Lpos
        Spos = S + b - Lpos
        Rpos = N-(Spos+Ipos)
        # Updating stats
        self.parentSite.incidence.append(Lpos)
        # Raises site infected flag and adds parent site to the epidemic history list.
        if not self.parentSite.infected: 
            if Lpos > 0:
                #if not self.parentSite.infected:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ipos)
        
        return [0,Ipos,Spos]

    def stepSIR_s(self,inits=(0,0,0),theta=0, npass=0,dist='poisson'):
        """
        Defines an stochastic model SIR:
        - inits = (E,I,S)
        - theta = infectious individuals from neighbor sites
        """
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else:
            E,I,S = inits
        N = self.parentSite.totpop
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        #parameter: beta,alpha,e,r,delta,b,w,p 
        Lpos_esp = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
        
        if dist == 'poisson':
            Lpos = poisson(Lpos_esp)
        elif dist == 'negbin':
            prob = I/(I+Lpos_esp) #convertin between parameterizations
            Lpos = negative_binomial(I,prob)
        self.parentSite.totalcases += Lpos #update number of cases   
        # Model
        Ipos = (1-r)*I + Lpos
        Spos = S + b - Lpos
        Rpos = N-(Spos+Ipos)
        # Updating stats
        self.parentSite.incidence.append(Lpos)
        if not self.parentSite.infected:
            if Lpos > 0:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ipos)            
        
        return [0,Ipos,Spos]
    
    def stepSEIS(self,inits=(0,0,0),theta=0, npass=0):
        """
        Defines the model SEIS:
        - inits = (E,I,S)
        - theta = infectious individuals from neighbor sites
        """
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else:
            E,I,S = inits
        N = self.parentSite.totpop
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        #parameters: beta,alpha,e,r,delta,b,w,p 
        Lpos = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
        self.parentSite.totalcases += Lpos #update number of cases
        #print N,E,I,S,Lpos,theta
        Epos = (1-e)*E + Lpos
        Ipos = e*E + (1-r)*I
        Spos = S + b - Lpos + r*I
        
        self.parentSite.incidence.append(Lpos)
        if not self.parentSite.infected:
            if Lpos > 0:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ipos)
        
        return [Epos,Ipos,Spos]
        
    def stepSEIS_s(self,inits=(0,0,0),theta=0, npass=0,dist='poisson'):
        """
        Defines an stochastic model SEIS:
        - inits = (E,I,S)
        - par = (Beta, alpha, E,r,delta,B,w,p) see docs.
        - theta = infectious individuals from neighbor sites
        """
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else:
            E,I,S = inits
        N = self.parentSite.totpop
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        #parameters: beta,alpha,e,r,delta,b,w,p
        Lpos_esp = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
        
        if dist == 'poisson':
            Lpos = poisson(Lpos_esp)
        elif dist == 'negbin':
            prob = I/(I+Lpos_esp) #converting between parameterizations
            Lpos = negative_binomial(I,prob)
        self.parentSite.totalcases += Lpos #update number of cases    
        Epos = (1-e)*E + Lpos
        Ipos = e*E + (1-r)*I
        Spos = S + b - Lpos + r*I
        
        self.parentSite.incidence.append(Lpos)
        if not self.parentSite.infected:
            if Lpos > 0:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ipos)
        
        return [Epos,Ipos,Spos]
    
    def stepSEIR(self,inits=(0,0,0),theta=0, npass=0):
        """
        Defines the model SEIR:
        - inits = (E,I,S)
        - par = (Beta, alpha, E,r,delta,B,w,p) see docs.
        - theta = infectious individuals from neighbor sites
        """
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else:
            E,I,S = inits
        N = self.parentSite.totpop
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        #parameters: beta,alpha,e,r,delta,B,w,p 
        Lpos = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
        self.parentSite.totalcases += Lpos #update number of cases
        #print N,E,I,S,Lpos,theta
        Epos = (1-e)*E + Lpos
        Ipos = e*E + (1-r)*I
        Spos = S + b - Lpos 
        Rpos = N-(Spos+Epos+Ipos)
        #self.parentSite.totpop = Spos+Epos+Ipos+Rpos
        self.parentSite.incidence.append(Lpos)
        if not self.parentSite.infected:
            if Lpos > 0:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ipos)
        
        return [Epos,Ipos,Spos]
    
    def stepSEIR_s(self,inits=(0,0,0),theta=0, npass=0,dist='poisson'):
        """
        Defines an stochastic model SEIR:
        - inits = (E,I,S)
        - par = (Beta, alpha, E,r,delta,B,w,p) see docs.
        - theta = infectious individuals from neighbor sites
        """
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else:
            E,I,S = inits
        N = self.parentSite.totpop
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        #parameters: beta,alpha,e,r,delta,B,w,p 
        Lpos_esp = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
        
        if dist == 'poisson':
            Lpos = poisson(Lpos_esp) #poisson(Lpos_esp)
##            if theta == 0 and Lpos_esp == 0 and Lpos > 0:  
##                print Lpos,Lpos_esp,S,I,theta,N,self.parentSite.sitename
        elif dist == 'negbin':
            prob = I/(I+Lpos_esp) #convertin between parameterizations
            Lpos = negative_binomial(I,prob)
        self.parentSite.totalcases += Lpos #update number of cases    
        Epos = (1-e)*E + Lpos
        Ipos = e*E + (1-r)*I
        Spos = S + b - Lpos 
        Rpos = N-(Spos+Epos+Ipos)
        #self.parentSite.totpop = Spos+Epos+Ipos+Rpos
        self.parentSite.incidence.append(Lpos)
        if not self.parentSite.infected:
            if Lpos > 0:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ipos)
        
        return [Epos,Ipos,Spos]
    
    def stepSIpRpS(self,inits,theta=0, npass=0):
        """
        calculates the model SIpRpS, and return its values (no demographics)
        - inits = (E,I,S)
        - theta = infectious individuals from neighbor sites
        """
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else:
            E,I,S = inits
        N = self.parentSite.totpop
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        # parameter: beta,alpha,e,r,delta,b,w,p
        Lpos = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
        self.parentSite.totalcases += Lpos #update number of cases
        # Model
        Ipos = (1-r)*I + Lpos
        Spos = S + b - Lpos + (1-delta)*r*I
        Rpos = N-(Spos+Ipos) + delta*r*I
        # Updating stats
        self.parentSite.incidence.append(Lpos)
        # Raises site infected flag and adds parent site to the epidemic history list.
        if not self.parentSite.infected: 
            if Lpos > 0:
                #if not self.parentSite.infected:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ipos)
        
        return [0,Ipos,Spos]
    
    def stepSIpRpS_s(self,inits=(0,0,0),theta=0, npass=0,dist='poisson'):
        """
        Defines an stochastic model SIpRpS:
        - inits = (E,I,S)
        - theta = infectious individuals from neighbor sites
        """
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else:
            E,I,S = inits
        N = self.parentSite.totpop
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        # parameter: beta,alpha,e,r,delta,B,w,p
        Lpos_esp = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
        
        if dist == 'poisson':
            Lpos = poisson(Lpos_esp)
        elif dist == 'negbin':
            prob = I/(I+Lpos_esp) #convertin between parameterizations
            Lpos = negative_binomial(I,prob)
        self.parentSite.totalcases += Lpos #update number of cases   
        # Model
        Ipos = (1-r)*I + Lpos
        Spos = S + b - Lpos + (1-delta)*r*I
        Rpos = N-(Spos+Ipos) + delta*r*I
        # Updating stats
        self.parentSite.incidence.append(Lpos)
        if not self.parentSite.infected:
            if Lpos > 0:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ipos)
        
        return [0,Ipos,Spos]
        
    def stepSEIpRpS(self,inits=(0,0,0),theta=0, npass=0):
        """
        Defines the model SEIpRpS:
        - inits = (E,I,S)
        - theta = infectious individuals from neighbor sites
        """
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else:
            E,I,S = inits
        N = self.parentSite.totpop
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        # parameter: beta,alpha,e,r,delta,b,w,p 
        
        Lpos = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
        self.parentSite.totalcases += Lpos #update number of cases
        #print N,E,I,S,Lpos,theta
        Epos = (1-e)*E + Lpos
        Ipos = e*E + (1-r)*I
        Spos = S + b - Lpos + (1-delta)*r*I
        Rpos = N-(Spos+Epos+Ipos) + delta*r*I
        #self.parentSite.totpop = Spos+Epos+Ipos+Rpos
        self.parentSite.incidence.append(Lpos)
        if not self.parentSite.infected:
            if Lpos > 0:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ipos)
        
        return [Epos,Ipos,Spos]
    
    def stepSEIpRpS_s(self,inits=(0,0,0),theta=0, npass=0,dist='poisson'):
        """
        Defines an stochastic model SEIpRpS:
        - inits = (E,I,S)
        - theta = infectious individuals from neighbor sites
        """
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else:
            E,I,S = inits
        N = self.parentSite.totpop
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        # parameter: beta,alpha,e,r,delta,b,w,p
        Lpos_esp = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
        
        if dist == 'poisson':
            Lpos = poisson(Lpos_esp)
        elif dist == 'negbin':
            prob = I/(I+Lpos_esp) #convertin between parameterizations
            Lpos = negative_binomial(I,prob)
        self.parentSite.totalcases += Lpos #update number of cases    
        Epos = (1-e)*E + Lpos
        Ipos = e*E + (1-r)*I
        Spos = S + b - Lpos + (1-delta)*r*I
        Rpos = N-(Spos+Epos+Ipos) + delta*r*I
        #self.parentSite.totpop = Spos+Epos+Ipos+Rpos
        self.parentSite.incidence.append(Lpos)
        if not self.parentSite.infected:
            if Lpos > 0:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ipos)
        
        return [Epos,Ipos,Spos]
    
    def stepSIpR(self,inits,theta=0, npass=0):
        """
        calculates the model SIpR, and return its values (no demographics)
        - inits = (E,I,S)
        - theta = infectious individuals from neighbor sites
        """
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else:
            E,I,S = inits
        N = self.parentSite.totpop
        R = N-E-I-S
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        #parameter: beta,alpha,e,r,delta,b,w,p
        Lpos = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
        Lpos2 = p*float(beta)*R*((I+theta)/(N+npass))**alpha
        self.parentSite.totalcases += Lpos+Lpos2 #update number of cases
        # Model
        Ipos = (1-r)*I + Lpos + Lpos2
        Spos = S + b - Lpos
        Rpos = N-(Spos+Ipos) - Lpos2
        # Updating stats
        self.parentSite.incidence.append(Lpos+Lpos2) #total cases
        self.parentSite.incidence2.append(Lpos2)  # secondary infections
        # Raises site infected flag and adds parent site to the epidemic history list.
        if not self.parentSite.infected: 
            if Lpos > 0:
                #if not self.parentSite.infected:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ipos)
        
        return [0,Ipos,Spos]
    
    def stepSIpR_s(self,inits=(0,0,0),theta=0, npass=0,dist='poisson'):
        """
        Defines an stochastic model SIpRs:
        - inits = (E,I,S)
        - theta = infectious individuals from neighbor sites
        """
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else:
            E,I,S = inits
        N = self.parentSite.totpop
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        #parameter: beta,alpha,e,r,delta,b,w,p
        R = N-E-I-S
        
        Lpos_esp = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
        Lpos2_esp = p*float(beta)*R*((I+theta)/(N+npass))**alpha
        
        if dist == 'poisson':
            Lpos = poisson(Lpos_esp)
            Lpos2 = poisson(Lpos2_esp)
        elif dist == 'negbin':
            prob = I/(I+Lpos_esp) #convertin between parameterizations
            Lpos = negative_binomial(I,prob)
            prob = I/(I+Lpos2_esp) #convertin between parameterizations
            Lpos2 = negative_binomial(I,prob)
        self.parentSite.totalcases += Lpos+Lpos2 #update number of cases   
        # Model
        Ipos = (1-r)*I + Lpos + Lpos2
        Spos = S + b - Lpos
        Rpos = N-(Spos+Ipos) - Lpos2
        # Updating stats
        self.parentSite.incidence.append(Lpos+Lpos2) #total cases
        self.parentSite.incidence2.append(Lpos2)  # secondary infections
        # Raises site infected flag and adds parent site to the epidemic history list.
        if not self.parentSite.infected:
            if Lpos > 0:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ipos)
        return [0,Ipos,Spos]
    
    def stepSEIpR(self,inits,theta=0, npass=0):
        """
        calculates the model SEIpR, and return its values (no demographics)
        - inits = (E,I,S)
        - theta = infectious individuals from neighbor sites
        """
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else:
            E,I,S = inits
        N = self.parentSite.totpop
        R = N-E-I-S
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        # parameters: beta,alpha,e,r,delta,b,w,p
        
        Lpos = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
        Lpos2 = p*float(beta)*R*((I+theta)/(N+npass))**alpha
        self.parentSite.totalcases += Lpos+Lpos2 #update number of cases
        # Model
        Epos = (1-e)*E + Lpos + Lpos2
        Ipos = e*E+ (1-r)*I 
        Spos = S + b - Lpos
        Rpos = N-(Spos+Ipos) - Lpos2
        # Updating stats
        self.parentSite.incidence.append(Lpos+Lpos2) #total cases
        self.parentSite.incidence2.append(Lpos2)  # secondary infections
        # Raises site infected flag and adds parent site to the epidemic history list.
        if not self.parentSite.infected: 
            if Lpos > 0:
                #if not self.parentSite.infected:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ipos)
        
        return [0,Ipos,Spos]
    
    def stepSEIpR_s(self,inits=(0,0,0),theta=0, npass=0,dist='poisson'):
        """
        Defines an stochastic model SEIpRs:
        - inits = (E,I,S)
        - theta = infectious individuals from neighbor sites
        """
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else:
            E,I,S = inits
        N = self.parentSite.totpop
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        # parameter: beta,alpha,e,r,delta,B,w,p        
        R = N-E-I-S
        
        Lpos_esp = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
        Lpos2_esp = p*float(beta)*R*((I+theta)/(N+npass))**alpha
        
        if dist == 'poisson':
            Lpos = poisson(Lpos_esp)
            Lpos2 = poisson(Lpos2_esp)
        elif dist == 'negbin':
            prob = I/(I+Lpos_esp) #convertin between parameterizations
            Lpos = negative_binomial(I,prob)
            prob = I/(I+Lpos2_esp) #convertin between parameterizations
            Lpos2 = negative_binomial(I,prob)
        self.parentSite.totalcases += Lpos+Lpos2 #update number of cases   
        # Model
        Epos = (1-e)*E + Lpos + Lpos2
        Ipos = e*E+ (1-r)*I
        Spos = S + b - Lpos
        Rpos = N-(Spos+Ipos) - Lpos2
        # Updating stats
        self.parentSite.incidence.append(Lpos+Lpos2) #total cases
        self.parentSite.incidence2.append(Lpos2)  # secondary infections
        # Raises site infected flag and adds parent site to the epidemic history list.
        if not self.parentSite.infected:
            if Lpos > 0:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ipos)
        
        return [0,Ipos,Spos]
        
    def stepSIRS(self,inits,theta=0, npass=0):
        """
        calculates the model SIRS, and return its values (no demographics)
        - inits = (E,I,S)
        - theta = infectious individuals from neighbor sites
        """
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else:
            E,I,S = inits
        N = self.parentSite.totpop
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        #parameter: beta,alpha,e,r,delta,b,w,p
        Lpos = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
        self.parentSite.totalcases += Lpos #update number of cases
        # Model
        Ipos = (1-r)*I + Lpos
        Spos = S + b - Lpos + w*R
        Rpos = N-(Spos+Ipos) - w*R
        # Updating stats
        self.parentSite.incidence.append(Lpos)
        # Raises site infected flag and adds parent site to the epidemic history list.
        if not self.parentSite.infected: 
            if Lpos > 0:
                #if not self.parentSite.infected:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ipos)
        
        return [0,Ipos,Spos]
    
    def stepSIRS_s(self,inits=(0,0,0),theta=0, npass=0,dist='poisson'):
        """
        Defines an stochastic model SIR:
        - inits = (E,I,S)
        - theta = infectious individuals from neighbor sites
        """
        if self.parentSite.parentGraph.simstep == 1: #get initial values
            E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
        else:
            E,I,S = inits
        N = self.parentSite.totpop
        for k, v in self.bp.items():
            exec('%s = %s'%(k, v))
        # parameter: beta,alpha,e,r,delta,b,w,p
        Lpos_esp = float(beta)*S*((I+theta)/(N+npass))**alpha #Number of new cases
        
        if dist == 'poisson':
            Lpos = poisson(Lpos_esp)
        elif dist == 'negbin':
            prob = I/(I+Lpos_esp) #convertin between parameterizations
            Lpos = negative_binomial(I,prob)
        self.parentSite.totalcases += Lpos #update number of cases   
        # Model
        Ipos = (1-r)*I + Lpos
        Spos = S + b - Lpos + w*R
        Rpos = N-(Spos+Ipos) - w*R
        # Updating stats
        self.parentSite.incidence.append(Lpos)
        if not self.parentSite.infected:
            if Lpos > 0:
                self.parentSite.infected = self.parentSite.parentGraph.simstep
                self.parentSite.parentGraph.epipath.append((self.parentSite.parentGraph.simstep,self.parentSite,self.parentSite.infector))
        #Migrating infecctious
        self.parentSite.migInf.append(Ipos)
        
        return [0,Ipos,Spos]
        
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
        
        Leng -- Length in kilometers of this route
        """
        if not isinstance(source, siteobj):
            raise TypeError, 'source received a non siteobj class object'
        if not isinstance(dest, siteobj):
            raise TypeError, 'destination received a non siteobj class object'
        self.dest = dest
        self.source = source
        self.sites = [source,dest]
        self.fmig = float(fmig) #daily migration from source to destination
        self.bmig = float(bmig) #daily migration from destination to source
        self.parentGraph = None
        self.length = Leng
        self.delay = 0
        self.ftheta = [] #time series of number of infected individuals travelling forward
        self.btheta = [] #time series of number of infected individuals travelling backwards
        dest.edges.append(self) #add itself to edge list of dest site
        source.edges.append(self) #add itself to edge list of source site
        

    def calcDelay(self):
        """
        calculate the Transportation delay given the speed and length.
        """
        if self.parentGraph.speed > 0:
            self.delay = int(float(self.length)/self.parentGraph.speed)
    
    def transportStoD(self):
        """
        Get infectious individuals commuting from source node and inform them to destination
        """
        theta,npass = self.source.getTheta(self.fmig,self.delay)
        self.ftheta.append(theta)
        self.dest.receiveTheta(theta,npass,self.source.sitename)
    def transportDtoS(self):
        """
        Get infectious individuals commuting from destination node and inform them to source
        """
        theta,npass = self.dest.getTheta(self.bmig,self.delay)
        self.btheta.append(theta)
        self.source.receiveTheta(theta,npass,self.dest.sitename)

    
    
class graph:
    """
    Defines a graph with sites and edges
    """
    def __init__(self,graph_name,digraph=0):
        self.name = graph_name
        self.digraph = digraph
        self.site_list = []
        self.edge_list = []
        self.speed = 0 # speed of the transportation system
        self.simstep = 1 #current step in the simulation
        self.maxstep = 100 #maximum number of steps in the simulation
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
        self.episize = 0 # total number of people infected
        self.epispeed = [] # new cities pre unit of time
        self.infectedcities = 0 #total number of cities infected.
        self.spreadtime = 0
        self. mediansurvival = None
        self.totVaccinated = 0
        self.totQuarantined = 0
        self.gr = None #This will be th visual graph representation object (DEPRECATED)
        self.dmap = 0 #draw the map in the background?
        self.printed = 0 #Printed the custom model docstring?

    def addSite(self, sitio):
        """
        Adds a site object to the graph. 
        It takes a siteobj object as its only argument and returns
        None.
        """

        if not isinstance(sitio, siteobj):
            raise Error, 'add_site received a non siteobj class object'

        self.site_list.append(sitio)
        sitio.parentGraph = self

    def dijkstra(self,G,start,end=None):
        """
        Find shortest paths from the start vertex to all
        vertices nearer than or equal to the end.
    
        The input graph G is assumed to have the following
        representation: A vertex can be any object that can
        be used as an index into a dictionary.  G is a
        dictionary, indexed by vertices.  For any vertex v,
        G[v] is itself a dictionary, indexed by the neighbors
        of v.  For any edge v->w, G[v][w] is the length of
        the edge.  This is related to the representation in
        <http://www.python.org/doc/essays/graphs.html>
        where Guido van Rossum suggests representing graphs
        as dictionaries mapping vertices to lists of neighbors,
        however dictionaries of edges have many advantages
        over lists: they can store extra information (here,
        the lengths), they support fast existence tests,
        and they allow easy modification of the graph by edge
        insertion and removal.  Such modifications are not
        needed here but are important in other graph algorithms.
        Since dictionaries obey iterator protocol, a graph
        represented as described here could be handed without
        modification to an algorithm using Guido's representation.
    
        Of course, G and G[v] need not be Python dict objects;
        they can be any other object that obeys dict protocol,
        for instance a wrapper in which vertices are URLs
        and a call to G[v] loads the web page and finds its links.
        
        The output is a pair (D,P) where D[v] is the distance
        from start to v and P[v] is the predecessor of v along
        the shortest path from s to v.
        
        Dijkstra's algorithm is only guaranteed to work correctly
        when all edge lengths are positive. This code does not
        verify this property for all edges (only the edges seen
        before the end vertex is reached), but will correctly
        compute shortest paths even for some graphs with negative
        edges, and will raise an exception if it discovers that
        a negative edge has caused it to make a mistake.
        """

        D = {}  # dictionary of final distances
        P = {}  # dictionary of predecessors
        Q = priorityDictionary()   # est.dist. of non-final vert.
        Q[start] = 0
        
        for v in Q:
            D[v] = Q[v]
            if v == end: break
            
            for w in G[v]:
                vwLength = D[v] + G[v][w]
                if w in D:
                    #print vwLength
                    if vwLength < D[w]:
                        raise ValueError, \
      "Dijkstra: found better path to already-final vertex"
                elif w not in Q or vwLength < Q[w]:
                    Q[w] = vwLength
                    P[w] = v

        return (D,P)
    
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
        if l==1:
            return match[0]
        elif l>1:
            return match
        else:
            return None


    def addEdge(self, graph_edge):
        """Adds an edge object to the graph.
        
        It takes a edge object as its only argument and returns
        None.
        """

        if not isinstance(graph_edge, edge):
            raise Error, 'add_edge received a non edge class object'

        if not graph_edge.source in self.site_list:
            raise Error, 'Edge source does not belong to the graph'

        if not graph_edge.dest in self.site_list:
            raise Error, 'Edge destination does not belong to the graph'
        self.edge_list.append(graph_edge)
        graph_edge.parentGraph = self
        graph_edge.calcDelay()
        

    def getGraphdict(self):
        """
        Generates a dictionary of the graph for use in the shortest path function.
        """
        G = {}
        for i in self.site_list:
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
        if l==1:
            return match[0]
        elif l>1:
            return match
        else:
            return None
    
    def getSiteNames(self):
        """
        returns list of site names for a given graph.
        """
        sitenames = [s.sitename for s in self.site_list]
        
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
        u = len(self.edge_list) - len(self.site_list)+ 1
        return u
    
    def shortestPath(self,G,start,end):
        """
        Find a single shortest path from the given start node
        to the given end node.
        The input has the same conventions as self.dijkstra().
        'G' is the graph's dictionary self.graphdict.
        'start' and 'end' are site objects.
        The output is a list of the vertices in order along
        the shortest path.
        """
        
        D,P = self.dijkstra(G,start,end)
        Path = []
        while 1:
            Path.append(end)
            if end == start: break
            end = P[end]
        Path.reverse()
        return Path
        
    def clearVisual(self):
        """
        Clear the visual graph display
        """
##        for o in self.gr.display.objects:
##            o.visible = 0

        self.gr.display.visible = 0
        del(self.gr)
        self.gr = None
    
    def viewGraph(self, mapa='limites.txt'):
        """
        Starts the Vpython display of the graph.
        """
        try:
            import dgraph
            self.gr = dgraph.Graph(0.04)
            
            Nlist = [dgraph.Node(3,(i.pos[1],i.pos[0],0)) for i in self.site_list]
            Elist = []
            for e in self.edge_list:
                s = self.site_list.index(e.source)
                d = self.site_list.index(e.dest)
                Elist.append(dgraph.RubberEdge(Nlist[s],Nlist[d],1,damping=0.7))
            
            self.gr.insertNodeList(Nlist)
            self.gr.insertEdgeList(Elist)
            self.gr.centerView()
            if self.dmap:
                m = dgraph.Map(mapa)
                self.gr.insertMap(m)
            
        except ImportError, v:
            print v
    
    def lightGRNode(self,node,color = 'r'):
        """
        Paints red the sphere corresponding to the node in the visual display
        """
        i = self.site_list.index(node)
        if color == 'r': 
            red = (self.maxstep-self.simstep)/float(self.maxstep)
            blue = 1-red**6
            self.gr.nodes[i].box.color = (red,0.,blue)
            node.painted = 1
        elif color == 'g':
            self.gr.nodes[i].box.color = (0.,1.,0.)
        
    
    def drawGraph(self):
        """
        Draws the network using pylab
        """
        from matplotlib.collections import LineCollection
        from matplotlib.colors import ColorConverter
        colorConverter = ColorConverter()
        names = [i.sitename for i in self.site_list]
        x = array([i.pos[1] for i in self.site_list])
        y = array([i.pos[0] for i in self.site_list])
        #edge data
        xs = array([e.source.pos[1] for e in self.edge_list])
        ys = array([e.source.pos[0] for e in self.edge_list])
        xd = array([e.dest.pos[1] for e in self.edge_list])
        yd = array([e.dest.pos[0] for e in self.edge_list])
        edge_list = [((a,b),(c,d)) for a,b,c,d in zip(xs,ys,xd,yd)]
        
        ax= axes()
        ax.set_xticks([])
        ax.set_yticks([])
        #plotting nodes
        node_plot = ax.scatter(x,y)
        node_plot.set_zorder(2)
        #Plotting edges
        kolor = colorConverter.to_rgba('k')
        ed_colors = [kolor for i in edge_list]
        edge_coll = LineCollection(edge_list,colors=ed_colors,linestyle='solid')
        edge_coll.set_zorder(1)
        ax.add_collection(edge_coll)
        #plotting labels
##        for x,y,l in zip(x,y,names):
##            ax.text(x,y,l,transform=ax.transData)
        minx = amin(x)
        maxx = amax(x)
        miny = amin(y)
        maxy = amax(y)
        w = maxx-minx
        h = maxy-miny
        padx, pady = 0.05*w, 0.05*h
        corners = (minx-padx, miny-pady), (maxx+padx, maxy+pady)
        ax.update_datalim( corners)

        ax.autoscale_view()
        
        #saving
        savefig('graph.png')
        close()
    def drawGraphR(self):
        """
        Draws the network using R
        """
        d=r.capabilities()
        if d['png']:
            device = r.png
            device('graph.png',width=733,height=550)
        elif d['jpeg']:
            device = r.jpeg
            device('graph.png',width=733,height=550)  
        else:
            device = r.postscript
            device('graph.png',width=733,height=550)
        # node data
        x = [i.pos[1] for i in self.site_list]
        y = [i.pos[0] for i in self.site_list]
        r.plot(x,y,axes=r.F,pch=16,xlab="",ylab="")
        
        #edge data
        xs = [e.source.pos[1] for e in self.edge_list]
        ys = [e.source.pos[0] for e in self.edge_list]
        xd = [e.dest.pos[1] for e in self.edge_list]
        yd = [e.dest.pos[0] for e in self.edge_list]
        for i in range(len(xs)):
            r.lines(r.c(xs[i],xd[i]),r.c(ys[i],yd[i]),lwd=0.5,col="gray")
        r.points(x,y,pch=16)
        r.dev_off()
    
    def getAllPairs(self):
        """
        Returns a distance matrix for the graph nodes where 
        the distance is the shortest path. Creates another
        distance matrix where the distances are the lengths of the paths.
        """
        if self.allPairs.any(): #don't run twice
            return self.allPairs
        if self.graphdict:
            g = self.graphdict
        else:
            g = self.getGraphdict()
            
        d = len(g)
        dm = zeros((d,d),float)
        ap = zeros((d,d),float)
        i = 0
        for sitei in g.iterkeys():
            j = 0
            for sitej in g.keys()[:i]: #calculates only the lower triangle
                sp = self.shortestPath(g,sitei,sitej)
                lsp = self.getShortestPathLength(sitei,sp) #length of the shortestpath
                self.shortPathList.append((sitei,sitej,sp,lsp))
                #fill the entire allpairs matrix
                ap[i,j] = ap[j,i] = len(sp)-1 
                dm[i,j] = dm[j,i] = lsp
                j += 1
            i += 1
        self.shortDistMatrix = dm
        #print ap,dm
        self.allPairs = ap
        return ap
    
    def getShortestPathLength(self,origin,sp):
        """
        Returns sp Length
        """
        Length = 0
        i=0
        for s in sp[:-1]:
            Length += s.getDistanceFromNeighbor(sp[i+1])
            i+=1
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
        try:
            if self.connmatrix.any(): return self.connmatrix #don't run twice
        except: pass
        if not self.graphdict: #this generates site neighbors lists
            self.getGraphdict()
        nsites = len(self.site_list)
        cm = zeros((nsites,nsites),float)
        for i,sitei in enumerate(self.site_list):
            for j, sitej in enumerate(self.site_list[:i]):#calculates only lower triangle
                if sitei == sitej: pass
                else:
                    cm[i,j] = float(sitej in sitei.neighbors)
                #map results to the upper triangle
                cm[j,i] = cm[i,j]
        #print sum(cm), type(cm)
        return cm
    
    def getWienerD(self):
        """
        Returns the Wiener distance for a graph.
        """
        if self.wienerD: # Check if it has been calculated.
            return self.wienerD
            
        if self.allPairs.any():
            return sum(self.allPairs.flat)
        
        return sum(self.getAllPairs().flat)
        
    def getMeanD(self):
        """
        Returns the mean distance for a graph.
        """
        if self.meanD:
            return self.meanD
         
        if self.allPairs.any():
            return mean(compress(greater(self.allPairs.flat,0),self.allPairs.flat))
        
        return mean(compress(greater(self.getAllPairs().flat,0),self.getAllPairs().flat))
        
        
    def getDiameter(self):
        """
        Returns the diameter of the graph: longest shortest path.
        """
        if self.diameter:
            return self.diameter
        
        if self.allPairs.any():
            return max(self.allPairs.flat)
        
        return max(self.getAllPairs().flat)
            
    
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
        
        iota = self.getLength()/self.getWeight()
        return iota
    
    def getWeight(self):
        """
        The weight of all nodes in the graph (W(G)) is the summation 
        of each node's order (o) multiplied by 2 for all orders above 1.
        """
        degrees = [i.getDegree() for i in self.site_list]
        W = sum([i*2 for i in degrees if i > 1]) + sum([i for i in degrees if i < 2])
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
            
        lsp = [len(i[2]) for i in self.shortPathList] #list of lenghts of shortest paths.
        lpidx = lsp.index(max(lsp))#position of the longest sp.
        lp = self.shortPathList[lpidx][2] #longest shortest path
        Dd = 0
        for i in range(len(lp)-1): #calculates distance in km along lp 
            Dd += lp[i].getDistanceFromNeighbor(lp[i+1])
        
        #pi = l/self.getDiameter()
        pi = l/Dd
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
        B = len(self.edge_list)/float(len(self.site_list))
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
        nsites = float(len(self.site_list))
        A = self.getCycles()/(2.*nsites - 5)
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
        nedg = float(len(self.edge_list))
        nsites = float(len(self.site_list))
        G = nedg/3*(nsites - 2)
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
        
        return [self.allPairs,self.cycles,self.wienerD,self.meanD,self.diameter,self.length,
                self.weight,self.iotaidx,self.piidx,self.betaidx,self.alphaidx,self.gammaidx,
                self.connmatrix]
    
    def plotDegreeDist(self,cum = False):
        """
        Plots the Degree distribution of the graph
        maybe cumulative or not.
        """
        nn = len(self.site_list)
        ne = len(self.edge_list)
        deglist = [i.getDegree() for i in self.site_list]
        if not cum:
            hist(deglist)
            title('Degree Distribution (N=%s, E=%s)'%(nn,ne))
            xlabel('Degree')
            ylabel('Frequency')
        else:
            pass
        savefig('degdist.png')
        close()
            
    def getMedianSurvival(self):
        """
        Returns the time taken by the epidemic to reach 50% of the nodes.
        """
        n = len(self.site_list)
        try:
            median = self.epipath[int(n/2)][0]
        except: # In the case the epidemic does not reach 50% of nodes
            median = 'NA'
        return median
    
    def getTotVaccinated(self):
        """
        Returns the total number of vaccinated.
        """
        tot = sum([i.nVaccinated for i in self.site_list])
        return tot
    
    def getTotQuarantined(self):
        """
        Returns the total number of quarantined individuals.
        """
        tot = sum([i.nQuarantined for i in self.site_list])
        return tot
    
    def getEpistats(self):
        """
        Returns a list of all epidemiologically related stats.
        """
        self.episize =self.getEpisize()
        self.epispeed = self.getEpispeed()
        self.infectedcities = self.getInfectedCities()
        self.spreadtime= self.getSpreadTime()
        self.mediansurvival = self.getMedianSurvival()
        self.totVaccinated = self.getTotVaccinated()
        self.totQuarantined = self.getTotQuarantined()
        
        return[self.episize,self.epispeed,self.infectedcities,
        self.spreadtime,self.mediansurvival,self.totVaccinated,self.totQuarantined]
        
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
        N = sum([site.totalcases for site in self.site_list])
        
        return N
            
    def getEpispeed(self):
        """
        Returns the epidemic spreading speed. 
        """
        tl = [i[0] for i in self.epipath]
        nspt = []
        for j in range(self.simstep):
            nspt.append(tl.count(j)) #new sites per time step
        #Speed = [nspt[i+1]-nspt[i] for i in range(len(nspt))]
        return nspt
    
    def getSpreadTime(self):
        """
        Returns the duration of the epidemic in units of time.
        """
        tl = [i[0] for i in self.epipath]
        if not tl:
            dur = 'NA'
        else:
            dur  = tl[-1]-tl[0]
        return dur
    
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

class line:
    """
    Basic line object containing attributes and methods common to all
    line objects.
    """
    def __init__(self,nodes):
        """
        define a line based on sequence of nodes.
        """
        pass
    def intersect(self):
        """
        finds out if this line intersects another
        """
        pass
    def xarea(self):
        """
        finds out if this line extends to more than one area.
        """
        pass

class area:
    """
    Basic area object containing attributes and methods common to all
    area objects.
    """
    def __init__(self,nodes):
        self.nodes = nodes

    def centroid(self):
        """
        calculates the centroid of the area.
        """
        pass
    def area(self):
        """
        calculates the area
        """
        pass

    def neighbors(self):
        """
        return neighbors
        """
        pass

    def isIsland(self):
        """
        return true if the area is an island, i.e. has only one nejghboor and is not on a border.
        """
        pass
    def borderSizeWith(self, area):
        """
        returns the size of the border with a given area.
        """
        pass
    def perimeter(self):
        """
        returns the perimeter of the area
        """
        pass


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
            raise IndexError, "smallest of empty priorityDictionary"
        heap = self.__heap
        while heap[0][1] not in self or self[heap[0][1]] != heap[0][0]:
            lastItem = heap.pop()
            insertionPoint = 0
            while 1:
                smallChild = 2*insertionPoint+1
                if smallChild+1 < len(heap) and \
                        heap[smallChild] > heap[smallChild+1]:
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

    def __setitem__(self,key,val):
        '''
        Change value stored in dictionary and add corresponding
        pair to heap.  Rebuilds the heap if the number of deleted 
        items grows too large, to avoid memory leakage.
        '''
        dict.__setitem__(self,key,val)
        heap = self.__heap
        if len(heap) > 2 * len(self):
            self.__heap = [(v,k) for k,v in self.iteritems()]
            self.__heap.sort()  # builtin sort likely faster than O(n) heapify
        else:
            newPair = (val,key)
            insertionPoint = len(heap)
            heap.append(None)
            while insertionPoint > 0 and \
                    newPair < heap[(insertionPoint-1)//2]:
                heap[insertionPoint] = heap[(insertionPoint-1)//2]
                insertionPoint = (insertionPoint-1)//2
            heap[insertionPoint] = newPair

    def update(self, other):
        for key in other.keys():
            self[key] = other[key]
    
    def setdefault(self,key,val):
        '''Reimplement setdefault to call our customized __setitem__.'''
        if key not in self:
            self[key] = val
        return self[key]
#---main----------------------------------------------------------------------------


#if __name__ == '__main__':
#    sitioA = siteobj("Penedo",2000)
#    sitioB = siteobj("Itatiaia",3020)
#    linhaA = edge(sitioA,sitioB,4)
#    sitioA.createModel((.3,.3,.3),(1,1))
#   sitioA.runModel()
    #lista_de_sitios = (i=siteobj(10) for i = range(10))