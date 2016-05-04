# ! /usr/bin/env python
"""
Model Management and simulation objects.
"""
import cPickle
import time
from copy import deepcopy
from numpy import *
from collections import OrderedDict
from argparse import ArgumentParser
import ConfigParser
import string
import json
import sqlite3
import os
import getpass
import MySQLdb
import numpy as np
from simobj import graph, edge, siteobj
import spread
from data_io import *
import epigdal
import __version__
import requests
# import pydevd
# pydevd.settrace('localhost', port=39347, stdoutToServer=True, stderrToServer=True)



#import pycallgraph




class simulate:
    """
    This class takes care of setting up the model, simulating it, and storing the results
    """

    def __init__(self, fname=None, host='localhost', port=3306, db='epigrass', user='epigrass', password='epigrass',
                 backend='sqlite', silent=False):
        #pycallgraph.start_trace()
        #        self.pool = multiprocessing.Pool()
        self.parallel = True
        self.host = host
        self.port = port
        self.usr = user
        self.db = db
        self.fname = fname
        self.backend = backend
        self.passw = password
        self.repname = None
        self.shapefile = None
        self.World = None
        self.shpout = True
        self.silent = silent
        self.dir = os.getcwd()
        sys.path.insert(0, self.dir)  #add current path to sys.path
        self.gui = 0  # True if this object was created by the gui
        self.now = time.asctime().replace(' ', '_').replace(':', '')  #current date and time
        self.modelName = os.path.split(self.fname)[-1].split('.')[0]
        self.config = self.loadModelScript(self.fname)
        self.evalConfig(self.config)
        if not self.outdir:
            self.outdir = outdir = 'outdata-' + self.modelName
        if not os.path.exists(self.outdir):
            os.mkdir(self.outdir)
        if self.shapefile:  #create world object if a shapefile is provided
            self.World = epigdal.World(*self.shapefile + [self.outdir])
        self.chkScript()
        self.encoding = 'utf-8'  #default encoding for strings in the sites and edges files
        self.round = 0  #No replicates
        sitios = loadData(self.sites, sep=',', encoding=self.encoding)
        ed = loadData(self.edges, sep=',', encoding=self.encoding)
        l = self.instSites(sitios)
        e = self.instEdges(l, ed)
        self.g = self.instGraph(self.modelName, 1, l, e)


    def loadModelScript(self, fname):
        """
        Loads the model specification from the text file.
        Returns a dictionary with keys of the form
        <section>.<option> and the corresponding values.
        """
        config = {}
        config = config.copy()
        cp = ConfigParser.SafeConfigParser()
        cp.read(fname)
        for sec in cp.sections():
            name = string.lower(sec)
            for opt in cp.options(sec):
                config[name + "." + string.lower(opt)] = string.strip(cp.get(sec, opt))
        return config

    def evalConfig(self, config):
        """
        Takes in the config dictionary and generates the global variables needed.
        """
        try:
            #WORLD
            #load Shapefile if specified
            if config['the world.shapefile']:
                self.shapefile = eval(config['the world.shapefile'])
            else:
                self.shapefile = []

            #self.layer = config['the world.vector layer']
            self.sites = config['the world.sites']  #file containing site info
            self.edges = config['the world.edges']  #file containing edge info
            if config['the world.encoding']:
                self.encoding = config['the world.encoding']  #encoding specification
            #Epidemiological model
            self.modtype = config['epidemiological model.modtype']
            #self.models = eval(config['epidemiological model.models'])
            #PARAMETERS
            self.beta = config['model parameters.beta']
            self.alpha = config['model parameters.alpha']
            self.e = config['model parameters.e']
            self.r = config['model parameters.r']
            self.delta = config['model parameters.delta']
            self.B = config['model parameters.b']
            self.w = config['model parameters.w']
            self.p = config['model parameters.p']
            #INITIAL CONDITIONS  (inits are string to evaluated inside siteobj.createmodel)
            #self.S = config['initial conditions.s']
            #self.E = config['initial conditions.e']
            #self.I = config['initial conditions.i']
            #EPIDEMIC EVENTS
            self.seed = eval(config['epidemic events.seed'])
            self.vaccinate = eval(config['epidemic events.vaccinate'])
            #self.quarantine = eval(config['epidemic events.quarantine'])

            #[TRANSPORTATION MODEL]
            self.doTransp = eval(config['transportation model.dotransp'])
            self.stochTransp = eval(config['transportation model.stochastic'])
            self.speed = eval(config['transportation model.speed'])

            #SIMULATION AND OUTPUT
            self.steps = eval(config['simulation and output.steps'])
            self.outdir = config['simulation and output.outdir']
            self.MySQLout = eval(config['simulation and output.mysqlout'])
            #            self.Rep = eval(config['simulation and output.report'])
            #            self.siteRep = eval(config['simulation and output.siterep'])
            self.replicas = eval(config['simulation and output.replicas'])
            self.randomize_seeds = eval(config['simulation and output.randseed'])
            self.Batch = eval(config['simulation and output.batch'])
        except KeyError, v:
            V = v.__str__().split('.')
            sys.exit("Please check the syntax of your '.epg' file.\nVariable %s, from section %s was not specified." % (
                V[1], V[0]))
        if self.replicas:
            #            self.Rep = 0 #Turns off reports
            self.Batch = []  #Turns off Batch mode
            self.round = 0  # Initialize replicate counter
            # generate dictionaries for parameters and inits
        self.inits = OrderedDict()
        self.parms = {}
        for k, v in config.items():
            if k.startswith('initial conditions'):
                self.inits[k.split('.')[-1]] = v
            elif k.startswith('model parameters'):
                self.parms[k.split('.')[-1]] = v
            else:
                pass

    def chkScript(self):
        """
        Checks the type of the variables on the script
        """
        self.Say("Checking syntax of model script... NOW")

        if not os.access(self.sites, os.F_OK):
            self.Say('Sites file %s does not exist, please check your script.' % self.sites)
            sys.exit()
        if not os.access(self.edges, os.F_OK):
            self.Say('Egdes file %s does not exist, please check your script.' % self.edges)
            sys.exit()
        if not self.modtype in ['SIS', 'SIS_s', 'SIR', 'SIR_s', 'SEIS', 'SEIS_s', 'SEIR', 'SEIR_s', 'SIpRpS',
                                'SIpRpS_s', 'SIpR,SIpR_s', 'Influenza', 'Custom']:
            self.Say('Model type %s is invalid, please check your script.' % self.modtype)

        self.Say('Script %s passed syntax check NOW.' % self.modelName)

    def deg2dec(self, coord):
        """
        converts lat/long to decimal
        """
        co = coord.split(':')
        if int(co[0]) < 0:
            result = float(co[0]) - float(co[1]) / 60 - float(co[2]) / 3600
        else:
            result = float(co[0]) + float(co[1]) / 60 + float(co[2]) / 3600

        return result


    def instSites(self, sitelist):
        """
        Instantiates and returns a list of siteobj instances, from a list of site specification
        as returned by data_io.loadData.
        Here the site specific events are passed to each site, and the site models are created.
        """
        header = sitelist.pop(0)
        ncols = len(header)
        objlist = []
        for site in sitelist:
            if len(site) != ncols:
                raise ValueError("This line in your sites file has a different number elements:\n%s" % str(site))
            if ':' in site[0]:
                lat = self.deg2dec(site[0])
                long = self.deg2dec(site[1])
            else:
                lat = float(site[0])
                long = float(site[1])
            objlist.append(siteobj(site[2], site[3], (lat, long), int(strip(site[4])),
                                   tuple([float(i.strip()) for i in site[5:]])))
        for o in objlist:
            if self.stochTransp:
                o.stochtransp = 1
            else:
                o.stochtransp = 0
            N = o.totpop  #local copy for reference on model creation
            values = o.values  #local copy for reference on model creation
            inits = OrderedDict()
            parms = {}
            #eval parms and inits
            for k, v in self.inits.items():
                inits[k] = eval(v)
            for k, v in self.parms.items():
                parms[k] = eval(v)

            if self.vaccinate:
                if self.vaccinate[0][0] == 'all':
                    o.vaccination = [self.vaccinate[0][1], self.vaccinate[0][2]]
                else:
                    for i in self.vaccinate:
                        if int(o.geocode) == i[0]:
                            o.vaccination = [i[1], float(i[2])]
                            #            if self.quarantine:
                            #                for i in self.quarantine:
                            #                    if int(o.geocode) == i[0]:
                            #                        o.quarantine == i[1:]

            if self.seed:
                #print type(o.geocode), type(self.seed[0])

                for j in self.seed:
                    if int(o.geocode) == j[0] or self.seed[0][0] == "all":
                        #self.Say("%s infected person(s) arrived at %s"%(j[2],o.sitename))
                        inits[j[1].lower()] += j[2]
                        o.createModel(self.modtype, self.modelName, v=values, bi=inits, bp=parms)
                    else:
                        o.createModel(self.modtype, self.modelName, v=values, bi=inits, bp=parms)
            else:
                o.createModel(self.modtype, self.modelName, v=values, bi=inits, bp=parms)
        return objlist

    def instEdges(self, sitelist, edgelist):
        """
        Instantiates and returns a list of edge objects,

        sitelist -- list of siteobj objects.

        edgelist -- list of edge specifications as returned by data_io.loadData.
        """
        header = edgelist.pop(0)
        #print [i.sitename for i in sitelist]
        objlist = []
        source = dest = None
        for edg in edgelist:
            #print edgelist.index(edg)
            if edg[5] == edg[6]:
                #ignore circular edges
                continue
            for site in sitelist:
                #print site.sitename
                if str(site.geocode) == edg[5]:
                    source = site
                    #print 'found source = ',source.sitename
                elif str(site.geocode) == edg[6]:
                    dest = site
                    #print 'found dest = ',dest.sitename
                if (source and dest):
                    #print 'next edge!'
                    break
            if not (source and dest):
                #print source ,dest
                sys.exit(
                    'One of the vertices on edge ' + edg[0] + '-' + edg[1] + ' could not be found on the site list')

            objlist.append(edge(source, dest, edg[2], edg[3], float(edg[4])))
            source = dest = None

        return objlist

    def instGraph(self, name, digraph, siteobjlist, edgeobjlist):
        """
        Instantiates and returns a graph object from a list of edge objects.
        """
        g = graph(name, digraph)
        g.speed = self.speed

        for j in siteobjlist:
            g.addSite(j)

        for i in edgeobjlist:
            g.addEdge(i)

        return g

    def randomizeSeed(self, option):
        """
        Generate and return a list of randomized seed sites
        to be used in a repeated runs scenario.
        Seed sites are sampled with a probability proportional to the
        log of their population size.
        option: if 1 randomize; if 2, return unrundomized sequence
        """
        if option == 1:
            poplist = [log10(site.totpop) for site in self.g.site_dict.itervalues()]
            lpl = len(poplist)
            popprob = array(poplist) / sum(poplist)  #acceptance probability
            u = floor(np.random.uniform(0, lpl, self.replicas))
            sites = []
            i = 0
            site_list = self.g.site_list
            while i < self.replicas:
                p = np.random.uniform(0, 1)
                if p <= popprob[int(u[i])]:
                    sites.append(site_list[int(u[i])])
                    i += 1
        elif option == 2:
            sites = self.g.site_list
        return sites

    def setSeed(self, seed, n=1):
        '''
        Resets the number of infected to zero in all nodes but seed,
        which get n infected cases.
        seed must be a siteobj object.
        '''
        #inits[self.seed[0][1].lower()] += 1
        seedvar = self.seed[0][1].lower()  #retrieve the name of the variable containing the seeds
        self.Say('seedvar= %s' % seedvar)
        site_list = self.g.site_list
        self.seed = [(seed.geocode, seedvar, n)]

        for site in site_list:
            if site.geocode == seed.geocode or seed.geocode == 'all':
                site.bi[seedvar] = n
                #                site.ts[0][seedpos] = n

                self.Say("%s infected case(s) arrived at %s" % (n, seed.sitename))
            else:
                site.bi[seedvar] = 0
                #                site.ts[0][seedpos] = 0

    def start(self):
        """
        Start the simulation
        """
        if '/' in self.modelName:
            self.modelName = os.path.split(self.modelName)[-1]
        #        print "====>", self.gui
        time.sleep(10)
        self.Say('Simulation starting.')
        start = time.time()
        self.runGraph(self.g, self.steps, transp=self.doTransp)
        elapsed = time.time() - start
        self.Say('Simulation lasted %s seconds.' % elapsed)
        if self.MySQLout:
            if self.backend == 'csv':
                self.outToCsv(self.modelName)
            else:
                self.outToDb(self.modelName)
        if self.shpout:
            self.outToShp()
        self.dumpData()
        spread.Spread(self.g, self.outdir, self.encoding)
        #self.saveModel(self.modelName)
        #pycallgraph.make_dot_graph(self.modelName+'_callgraph.png')


    def createDataFrame(self, site):
        """
        Saves the time series *site.ts* to outfile as specified on the
        model script.
        """
        data = array(site.ts, float)
        inc = site.incidence
        f = open(self.outdir + self.outfile, 'w')
        f.write('time,E,I,S,incidence\n')
        try:
            for t, i in enumerate(data):
                j = [str(k) for k in i]
                line = str(t) + ','.join(j) + str(inc[t]) + '\n'
                f.write(line)
        finally:
            f.close()

        return 'E,I,S\n' + tss


    def outToShp(self):
        """
        Creates Data Layers in shapefile format
        """
        if not self.World:
            return
        #Initialize world output layers
        self.Say("REading Nodes from shapefile...")
        self.World.get_node_list(self.World.ds.GetLayerByName(self.World.layerlist[0]))
        self.Say("Done reading nodes!")
        self.Say("Creating Nodes shapefile...")
        self.World.create_node_layer()
        self.Say("Done creating Nodes shapefile!")
        elist = [(gcs[0], gcs[1], sum(e.ftheta), sum(e.btheta)) for gcs, e in self.g.edge_dict.iteritems()]
        self.Say("Creating Edges shapefile...")
        self.World.create_edge_layer(elist)
        self.Say("Done creating Edges shapefile!")
        #Generate site epidemic stats
        varlist = ["prevalence", "totalcases", "arrivals", "population"]
        sitestats = [(site.geocode, float(site.totalcases) / site.totpop, site.totalcases, sum(site.thetahist),
                      float(site.totpop)) for site in self.g.site_dict.itervalues()]
        names = {k: v.sitename for k, v in self.g.site_dict.iteritems()}

        self.Say("Creating Data shapefile...")
        self.World.create_data_layer(varlist, sitestats)
        self.Say("Done creating Data shapefile!")
        #Generate the kml too.
        self.out_to_kml(names)

        self.Say("Done creating KML files!")
        #close files
        self.World.close_sources()

    def out_to_kml(self, names):
        """
        Generates output to kml files
        """
        self.Say("Creating KML output files...")
        lr = self.World.datasource.GetLayer(0)
        k = epigdal.KmlGenerator()
        k.addNodes(lr, names)
        k.writeToFile(self.outdir)
        site_list = self.g.site_list
        site_dict = self.g.site_dict
        # Temporarily disabled animation output due to the sheer size of the kmz files
        if len(site_dict) * len(site_dict.values()[0].ts) < 20000:  # Only reasonably sized animations
            for i, v in enumerate(site_dict.values()[0].vnames):
                ka = epigdal.AnimatedKML(os.path.join(self.outdir, 'Data.kml'), extrude=True)
                data = [(str(site.geocode), t, p[i]) for site in site_dict.itervalues() for t, p in enumerate(site.ts)]
                ka.add_data(data)
                ka.save(v + '_animation')
                self.Say(v + '_animation')
                del ka
        else:
            self.Say("Simulation too large to export as kml.")

        self.Say("Done creating KML files!")

    def series_to_JSON(self):
        """
        Saves timeseries to JSON for uploading to epigrass web
        """
        self.Say('Saving series to JSON')
        series = {}
        for gc, s in self.g.site_dict.iteritems():
            ts = np.array(s.ts)
            sdict = {}
            for i, vn in enumerate(s.vnames):
                sdict[vn] = ts[:, i].tolist()
            series[gc] = sdict
        with open('series.json', 'w') as f:
            json.dump(series, f)

    def writeMetaCSV(self, table):
        """
        Writes a meta CSV table
        """
        if not self.outdir == os.getcwd():
            os.chdir(self.outdir)
        f = open(table + '_meta', 'w')
        cfgitems = self.config.items()
        h = ';'.join([k.strip().replace(' ', '_').replace('.', '$') for k, v in cfgitems])
        l = ';'.join([v.split('#')[0] for k, v in cfgitems])
        f.write(h + '\n')
        f.write(l + '\n')
        f.close()
        os.chdir(self.dir)

    def outToCsv(self, table):
        """
        Save simulation results in csv file.
        """
        if not self.outdir == os.getcwd():
            os.chdir(self.outdir)
        tablee = table + "_" + self.now + "_e.tab"  #edgetable name
        table += "_" + self.now + ".tab"  #sitetable name
        f = open(table, "w")
        head = ['geocode', 'time', 'totpop', 'name',
                'lat', 'longit']
        headerwritten = False
        for site in self.g.site_dict.itervalues():
            t = 0
            regb = [str(site.geocode), str(t), str(site.totpop),
                    site.sitename.replace('"', '').encode('ascii', 'replace'),
                    str(site.pos[0]), str(site.pos[1])
            ]
            if site.values:
                for n, v in enumerate(site.values):
                    head.append('values%s' % n)
                    regb.append(str(v))
            #print site.sitename, site.ts
            ts = array(site.ts[1:])  #remove init conds so that ts and inc are the same size
            head.extend(['incidence', 'arrivals'])
            for n, v in enumerate(site.vnames):
                head.append(str(v))
            for i in ts:
                reg = deepcopy(regb)
                reg.extend([str(site.incidence[t]), str(site.thetahist[t])])
                reg[1] = str(t)
                for n, v in enumerate(site.vnames):
                    reg.append(str(i[n]))
                if not headerwritten:
                    h = ",".join(head)
                    f.write(h + '\n')
                    headerwritten = True
                f.write(','.join(reg) + '\n')
                t += 1
        f.close()
        #inserting data in edges file
        g = open(tablee, 'w')
        t = 0
        head = ['source_code', 'dest_code', 'time', 'ftheta', 'btheta']
        ehw = False
        for e in self.g.edge_list:
            for f, b in zip(e.ftheta, e.btheta):
                if not ehw:
                    g.write(','.join(head) + '\n')
                    ehw = True
                ereg = [e.source.geocode, e.dest.geocode, t, f, b]
                ereg = [str(i) for i in ereg]
                g.write(','.join(ereg) + '\n')
                t += 1
        g.close()
        os.chdir(self.dir)

    #    def outToODb(self,table,mode='b'):
    #        """
    #        Insert simulation results in a database using sqlobject.
    #        if mode = b, do batch inserts
    #        if mode = p, do parallel inserts
    #        """
    #        #set connection parameters
    #        try:
    #            DO.Connect(self.backend.lower(),self.usr,self.passw,self.host,self.port,self.db)
    #            self.Say('Saving data on %s database...'%self.backend)
    #        except:
    #            self.Say('Database Connection Failed')
    #        #basic connection variables
    #        name = table+'_'+self.now
    #        self.outtable = name
    #
    #        DO.Site.sqlmeta.table = name
    #        DO.Edge.sqlmeta.table = name+'e'
    #        if self.backend.lower()=='sqlite':
    #            DO.Site.sqlmeta.createSQL = {'sqlite':['PRAGMA synchronous=OFF;','PRAGMA default_cache_size=12000000;']}
    #            DO.Site._connection.commit()
    #            DO.Edge.sqlmeta.createSQL = {'sqlite':['PRAGMA synchronous=OFF;','PRAGMA default_cache_size=12000000;']}
    #            DO.Edge._connection.commit()
    #        #adding columns to sites table
    #        try: #Only add if they don't exist. On Batch runs this will catch the add error
    #            DO.Site.sqlmeta.addColumn(StringCol('incidence'))
    #            DO.Site.sqlmeta.addColumn(StringCol('arrivals'))
    #        except: pass
    #        if self.g.site_list[0].values:#add columns for 'values' variables
    #            for i in xrange(len(self.g.site_list[0].values)):
    #                try:
    #                    DO.Site.sqlmeta.addColumn(StringCol('values%s'%i))
    #                except: pass
    #        for s in self.g.site_list[0].vnames: #add columns for state variables
    #            try:
    #                DO.Site.sqlmeta.addColumn(StringCol(s))
    #            except: pass
    #        #creating tables
    #        DO.Site.createTable()
    #        DO.Edge.createTable()
    #        #saving pickle of adjacency matrix
    #        matname = 'adj_'+self.modelName # table
    #        adjfile = open(matname,'w')
    #        cPickle.dump(self.g.getConnMatrix(),adjfile)
    #        adjfile.close()
    #        #calling insert function
    #        if mode == 'b':
    #            self.batchInsert()
    #        elif mode == 'p':
    #            self.parInsert()
    #
    #    def batchInsert(self):
    #        """
    #        Do the inserts all at once. After the simulation is done
    #        """
    #        #inserting data in sites table
    #        for site in self.g.site_list:
    #            dicin={
    #            'geocode':site.geocode,
    #            'lat':float(site.pos[0]),
    #            'longit':float(site.pos[1]),
    #            'name':site.sitename.replace('"','').encode('ascii','replace'),
    #            'totpop':int(site.totpop)}
    #            if site.values:
    #                for n,v in enumerate(site.values):
    #                    #print v,type(v)
    #                    dicin['values%s'%n] = str(v)
    #            ts = array(site.ts[1:]) #remove init conds so that ts and inc are the same size
    #            t = 0
    #            for i in ts:
    #                dicin['incidence']= str(site.incidence[t])
    #                dicin['arrivals'] = str(site.thetahist[t])
    #                dicin['time'] = t
    #                for n,v in enumerate(site.vnames):
    #                    #print i[n],type( i[n])
    #                    dicin[v] = str(i[n])
    #                    DO.Site(**dicin)
    #                t += 1
    #        #DO.Site._connection.commit()
    #        #inserting data in edges table
    #        for e in self.g.edge_list:
    #            rlist = []
    #            edicin={
    #            'source_code':e.source.geocode,
    #            'dest_code':e.dest.geocode}
    #            t=0
    #            for f,b in zip(e.ftheta,e.btheta):
    #                edicin['time'] = t
    #                edicin['ftheta'] = f
    #                edicin['btheta'] = b
    #                rlist.append(edicin)
    #                t += 1
    #            insobj = DO.sqlbuilder.Insert(DO.Edge.sqlmeta.table,valueList=rlist)
    #            DO.Edge._connection.queryAll(DO.Edge._connection.sqlrepr(insobj))
    #            #DO.Edge._connection.commit()
    #
    #    def parInsert(self):
    #        """
    #        do the insertions in a separate process.
    #        """
    #        pid = os.fork()
    #        if pid:
    #            #parent process get on with the simulation
    #            return
    #        else:
    #        #child process inserts data in sites table
    #            time.sleep(1+self.g.simstep)
    #            for site in self.g.site_list:
    #                dicin={
    #                'geocode':site.geocode,
    #                'lat':float(site.pos[0]),
    #                'longit':float(site.pos[1]),
    #                'name':site.sitename.replace('"','').encode('ascii','replace'),
    #                'totpop':int(site.totpop)}
    #                if site.values:
    #                    for n,v in enumerate(site.values):
    #                        #print v,type(v)
    #                        dicin['values%s'%n] = str(v)
    #                ts = array(site.ts[1:]) #remove init conds so that ts and inc are the same size
    #                t = self.g.simstep
    #                dicin['incidence']= str(site.incidence[t])
    #                dicin['arrivals'] = str(site.thetahist[t])
    #                dicin['time'] = t
    #                for n,v in enumerate(site.vnames):
    #                    #print i[n],type( i[n])
    #                    dicin[v] = str(i[n])
    #                DO.Site(**dicin)
    #            DO.Site._connection.commit()
    #            #inserting data in edges table
    #            for e in self.g.edge_list:
    #                edicin={
    #                'source_code':e.source.geocode,
    #                'dest_code':e.dest.geocode}
    #                edicin['time'] = t
    #                edicin['ftheta'] = e.ftheta[t]
    #                edicin['btheta'] = e.btheta[t]
    #                DO.Edge(**edicin)
    #            DO.Edge._connection.commit()
    #            sys.exit("commit successful")

    def writeMetaTable(self, table):
        """
        Creates a Meta-Info Table on the database with the contents of the .epg file
        """
        try:
            table = table + '_meta'
            if self.backend.lower() == "mysql":
                con = MySQLdb.connect(host=self.host, port=self.port,
                                      user=self.usr, passwd=self.passw, db=self.db)
            elif self.backend.lower() == "sqlite":
                if not self.outdir == os.getcwd():
                    os.chdir(self.outdir)
                con = sqlite3.connect("Epigrass.sqlite")
                os.chdir(self.dir)
            # Create table
            sqlstr1 = "CREATE TABLE %s(" % table
            vars = []
            cfgitems = self.config.items()
            for k, v in cfgitems:
                vars.append(k.strip().replace(' ', '_').replace('.', '$'))
            sqlstr2 = ', '.join(["%s text" % i for i in vars])
            Cursor = con.cursor()
            Cursor.execute(sqlstr1 + sqlstr2 + ');')
            #doing inserts
            values = [v.split('#')[0] for k, v in cfgitems]
            #            for k, v in cfgitems:
            #                v = v.split('#')[0]
            #                if not v:
            #                    v = ' '
            #                values.append()
            str3 = ','.join(['"%s"' % i for i in values]) + ')'
            sqlstr3 = '''INSERT INTO %s VALUES(%s''' % (table, str3)
            #print sqlstr3
            Cursor.execute(sqlstr3)
        finally:
            if con:
                con.commit()
                con.close()

    def outToDb(self, table):
        """
        Insert simulation results on a mysql or SQLite table
        :param table: Table name
        """

        if self.backend.lower() == "mysql":
            self.Say('Saving data on MySQL...')
        elif self.backend.lower() == "sqlite":
            self.Say('Saving data on SQLite...')

        con = None
        try:
            table = table + '_' + self.now
            self.writeMetaTable(table)
            self.outtable = table
            if self.backend.lower() == "mysql":
                con = MySQLdb.connect(host=self.host, port=self.port,
                                      user=self.usr, passwd=self.passw, db=self.db)
            elif self.backend.lower() == "sqlite":
                if not self.outdir == os.getcwd():
                    os.chdir(self.outdir)
                con = sqlite3.connect("Epigrass.sqlite")
                os.chdir(self.dir)
            # Define number of variables to be stored
            nvar = len(self.g.site_dict.values()[0].ts[
                -1]) + 4  # state variables,  plus coords, plus incidence, plus infected arrivals.
            str1 = '`%s` FLOAT(9),' * nvar  # nvar variables in the table
            str1lite = '%s REAL,' * nvar  # nvar variables in the SQLite table
            varnames = ['lat', 'longit'] + list(self.g.site_dict.values()[0].vnames) + ['incidence'] + ['Arrivals']
            #            print nvar, varnames, str1
            print nvar, len(varnames)
            str1 = str1[:-1] % tuple(varnames)  #insert variable names (MySQL)
            str1lite = str1lite[:len(str1lite) - 1] % tuple(varnames)  #insert variable names (SQLITE)
            Cursor = con.cursor()
            str2 = """CREATE TABLE %s(
            `geocode` INT( 9 )  ,
            `time` INT( 9 ) ,
            `name` varchar(128) ,
            """ % table
            str2lite = """CREATE TABLE %s(
            geocode INTEGER  ,
            time INTEGER ,
            name TEXT ,
            """ % table
            sql = str2 + str1 + ');'
            sqlite = str2lite + str1lite + ');'

            if self.backend.lower() == "mysql":
                Cursor.execute(sql)
                str3 = (nvar + 3) * '%s,'
                str3 = str3[:-1] + ')'
            elif self.backend.lower() == "sqlite":
                Cursor.execute(sqlite)
                str3 = (nvar + 3) * '?,'
                str3 = str3[:-1] + ')'
            sql2 = 'INSERT INTO %s' % table + ' VALUES(' + str3
            nvalues = []
            for site in self.g.site_dict.itervalues():
                geoc = site.geocode
                lat = site.pos[0]
                long = site.pos[1]
                name = site.sitename
                ts = array(site.ts[1:])  #remove init conds so that ts and inc are the same size
                inc = site.incidence
                thist = site.thetahist
                t = 0
                for incid, flow in zip(inc, thist):
                    tstep = str(t)
                    flow = float(thist[t])
                    nvalues.append(tuple([geoc, tstep, name] + [lat, long] + list(ts[t]) + [incid] + [flow]))
                    t += 1
            Cursor.executemany(sql2, nvalues)
            #Creating a table for edge data
            self.etable = etable = table + 'e'
            esql = """CREATE TABLE %s(
            `source_code` INT( 9 )  ,
            `dest_code` INT( 9 )  ,
            `time` INT( 9 ) ,
            `ftheta` FLOAT(9) ,
            `btheta` FLOAT(9) );""" % etable
            esqlite = """CREATE TABLE %s(
            source_code INTEGER  ,
            dest_code INTEGER  ,
            time INTEGER ,
            ftheta REAL ,
            btheta REAL );""" % etable

            if self.backend.lower() == "mysql":
                Cursor.execute(esql)
                esql2 = 'INSERT INTO %s' % etable + ' VALUES(%s,%s,%s,%s,%s)'
            elif self.backend.lower() == "sqlite":
                Cursor.execute(esqlite)
                esql2 = 'INSERT INTO %s' % etable + ' VALUES(?,?,?,?,?)'
            values = []
            for gcs, e in self.g.edge_dict.iteritems():
                s = gcs[0]
                d = gcs[1]
                t = 0
                for f, b in zip(e.ftheta, e.btheta):
                    values.append((s, d, t, f, b))
                    t += 1
            Cursor.executemany(esql2, values)


        finally:
            if con:
                con.close()
        #saving pickle of adjacency matrix
        matname = 'adj_' + self.modelName  # table
        fname = os.path.join(self.outdir, matname)
        adjfile = open(fname, 'w')
        cPickle.dump(self.g.getConnMatrix(), adjfile)
        adjfile.close()

    def criaAdjMatrix(self):
        # saving the adjacency  matrix
        codeslist = [str(i.geocode) for i in self.g.site_dict.itervalues()]
        if not os.path.exists('adjmat.csv'):
            self.Say('Saving the adjacency  matrix...')
            am = self.g.getConnMatrix()
            amf = open('adjmat.csv', 'w')
            amf.write(','.join(codeslist) + '\n')
            for row in am:
                row = [str(i) for i in row]
                amf.write(','.join(row) + '\n')
            amf.close()
            self.Say('Done!')

    def dumpData(self):
        """
        Dumps data as csv (comma-separated-values)
        """
        self.Say("Starting simulation Analysis")
        curdir = os.getcwd()
        if not self.outdir == curdir:
            os.chdir(self.outdir)

        codeslist = self.g.site_dict.keys()
        self.criaAdjMatrix()
        #saving the shortest path matrices
        #        if not os.path.exists('spmat.csv'):
        #            self.Say('Calculating the shortest path matrices...')
        #            ap = self.g.getAllPairs()
        #            f = open('ap','w')
        #            cPickle.dump(ap,f)
        #            f.close()
        #            spd = self.g.shortDistMatrix
        #            apf = open ('spmat.csv','w')
        #            apf.write(','.join(codeslist)+'\n')
        #            spdf = open ('spdmat.csv','w')
        #            spdf.write(','.join(codeslist)+'\n')
        #            for row in ap:
        #                row = [str(i) for i in row]
        #                apf.write(','.join(row)+'\n')
        #            apf.close()
        #            for row in spd:
        #                row = [str(i) for i in row]
        #                spdf.write(','.join(row)+'\n')
        #            spdf.close()
        #            print 'Done!'

        #Saving epidemic path
        self.Say('Saving Epidemic path...')
        if self.round:
            epp = codecs.open('epipath%s.csv' % str(self.round), 'w', self.encoding)
        else:
            epp = codecs.open('epipath.csv', 'w', self.encoding)
        epp.write('time,site,infector\n')
        for i in self.g.epipath:
            #print i
            site = self.g.site_dict[i[1]]
            infectors = i[-1]
            # sorting infectors by number of infective contributed
            if len(infectors):
                reverse_infectors = infectors.items()
                reverse_infectors.sort(key=lambda t: t[1])
                mli = reverse_infectors[-1][0].sitename  #Most likely infector
            else:
                mli = 'NA'
            #print i[1].sitename, type(i[1].sitename), mli
            epp.write(str(i[0]) + ',' + site.sitename + ',' + mli + '\n')
        epp.close()
        self.Say('Done!')
        self.g.save_topology('network.graphml')

        #saving Epistats
        self.Say('Saving Epidemiological results...')
        stats = [str(i) for i in self.g.getEpistats()]

        seed = [s for s in self.g.site_dict.itervalues() if s.geocode == self.seed[0][0] or self.seed[0][0] == 'all'][0]
        stats.pop(1)  #Remove epispeed which is a vector
        if os.path.exists('epistats.csv'):
            stf = codecs.open('epistats.csv', 'a', self.encoding)  #append to file
        else:
            stf = codecs.open('epistats.csv', 'w', self.encoding)  #create a new file
            stf.write(
                'seed,name,size,infected_sites,spreadtime,median_survival,totvaccinated,totquarantined,seeddeg,seedpop\n')
        ##            stf.write('seed,name,size,infected_sites,spreadtime,median_survival,totvaccinated,totquarantined,seeddeg,seedpop\n')
        #scent = str(seed.getCentrality())
        #sbetw = str(seed.getBetweeness())
        #sthidx = str(seed.getThetaindex())
        sdeg = str(seed.getDegree())
        spop = str(seed.totpop)
        sname = seed.sitename
        sstats = '%s,%s' % (sdeg, spop)
        #        sstats = '%s,%s,%s,%s,%s'%(scent,sbetw,sthidx,sdeg,spop)
        stf.write(str(self.seed[0][0]) + ',' + sname + ',' + ','.join(stats) + ',' + sstats + '\n')
        stf.close()
        self.Say('Done saving!')

        #Saving site stats
        self.Say('Saving site statistics...')
        #self.g.getAllPairs()
        if os.path.exists('sitestats.csv'):
            sitef = codecs.open('sitestats.csv', 'a', self.encoding)  #append to file
        else:
            sitef = codecs.open('sitestats.csv', 'w', self.encoding)

        #sitef.write('round,geocode,name,infection_time,degree,centrality,betweeness,theta_index,distance,seed,seedname\n')
        sitef.write('round,geocode,name,infection_time,degree,seed,seedname\n')
        for s in self.g.site_dict.itervalues():
            degree = str(s.getDegree())
            #central = str(s.getCentrality())
            #bet = str(s.getBetweeness())
            #thidx = str(s.getThetaindex())
            seedgc = str(self.seed[0][0])
            seedname = seed.sitename
            #            f = open('ap','r')
            #            ap = cPickle.load(f)
            #            f.close()
            #            distseed = str(ap[codeslist.index(str(s.geocode)),codeslist.index(str(self.seed[0][0]))])
            it = str(s.infected)  #infection time
            if it == 'FALSE':
                it = 'NA'

            #            sitef.write(str(self.round)+','+str(s.geocode)+','+s.sitename+','+it+','+degree+','+central+','+bet+','+thidx+','+distseed+','+seedgc+','+seedname+'\n')
            sitef.write(str(self.round) + ',' + str(
                s.geocode) + ',' + s.sitename + ',' + it + ',' + degree + ',' + seedgc + ',' + seedname + '\n')

        # Saving series to JSON
        self.series_to_JSON()
        os.chdir(curdir)

        self.Say('Done saving data!')

    def saveModel(self, fname):
        """
        Save the fully specified graph.
        """
        f = open(fname, 'w')
        cPickle.dump(self.g, f)
        f.close()

    def loadModel(self, fname):
        """
        Loads a pre-saved graph.
        """
        g = cPickle.load(fname)
        return g


    def runGraph(self, graphobj, iterations=1, transp=0):
        """
        Starts the simulation on a graph.
        """
        g = graphobj
        g.maxstep = iterations
        sites = graphobj.site_dict.values()
        edges = graphobj.edge_dict.values()
        #        g.sites_done = 0

        if transp:
            for n in xrange(iterations):
                print
                "==> {}\r".format(g.simstep),
                results = [i.runModel(self.parallel) for i in sites]
                if self.parallel:
                    [r.wait() for r in results]
                for j in edges:
                    j.migrate()
                if self.gui:
                    self.gui.stepLCD.display(g.simstep)
                    self.gui.app.processEvents()
                g.simstep += 1
                g.sites_done = 0
        else:
            for n in xrange(iterations):
                for i in sites:
                    i.runModel(self.parallel)
                if self.gui:
                    self.gui.stepLCD.display(g.simstep)
                    self.gui.app.processEvents()
                    self.gui.RT.mutex.lock()
                    self.gui.RT.emit(self.gui.QtCore.SIGNAL("drawStep"), g.simstep,
                                     dict([(s.geocode, s.incidence[-1]) for s in sites]))
                    self.gui.RT.mutex.unlock()
                g.simstep += 1

    def Say(self, string):
        """
        Exits outputs messages to the console or the gui accordingly
        """
        if self.gui:
            self.gui.textEdit1.insertPlainText(string + '\n''')
        else:
            if self.silent:
                return
            print
            string + '\n'


def storeSimulation(S, usr, passw, db='epigrass', host='localhost', port=3306):
    """
    store the Simulate object *s* in the epigrass database
    to allow distributed runs. Currently not working.
    """
    now = time.asctime().replace(' ', '_').replace(':', '')
    table = 'Model_' + S.modelName + now
    con = MySQLdb.connect(host=host, port=port, user=usr, passwd=passw, db=db)
    Cursor = con.cursor()
    sql = """CREATE TABLE %s(
        `simulation` BLOB);""" % table
    Cursor.execute(sql)
    blob = cPickle.dumps(S)
    sql2 = 'INSERT INTO %s' % table + ' VALUES(%s)'
    Cursor.execute(sql2, blob)
    con.close()


def onStraightRun(args):
    """
    Runs the model from the commandline
    """
    if args.backend == "mysql":
        S = simulate(fname=args.epg[0], host=args.dbhost, user=args.dbuser, password=args.dbpass, backend=args.backend)
    else:
        S = simulate(fname=args.epg[0], backend=args.backend)
    S.parallel = args.parallel
    if not S.replicas:
        S.start()
        spread.Spread(S.g)
    else:
        repRuns(S)

    if S.Batch:
        S.Say('Simulation Started.')

        # run the batch list
        for i in S.Batch:
            #Makes sure it comes back to original directory before opening models in the batch list
            os.chdir(S.dir)
            #delete the old graph object to save memory
            S.graph = None
            # Generates the simulation object
            T = simulate(fname=i, host=S.host, user=S.usr, password=S.passw, backend=S.backend)

            S.Say('starting model %s' % i)
            T.start()  # Start the simulation


#            spread.Spread(T.g)

def repRuns(S):
    """
    Do repeated runs
    """
    randseed = S.randomize_seeds
    fname = S.fname
    host = S.host
    user = S.usr
    password = S.passw
    backend = S.backend
    nseeds = S.seed[0][2]  #number o individual to be used as seeds
    S.Say("Replication type: ", randseed)
    if randseed:
        seeds = S.randomizeSeed(randseed)
    reps = S.replicas
    for i in xrange(reps):
        S.Say("Starting replicate number %s" % i)
        S = simulate(fname=fname, host=host, user=user, password=password, backend=backend)
        if randseed:
            S.setSeed(seeds[i], nseeds)
        S.round = i
        S.shpout = False
        S.start()
        del S


def upload_model(args):
    """
    Uploads Model specification, auxiliary files and
    :return:
    """
    username = raw_input("Enter your epigrass Web User id:")
    passwd = getpass("Enter your Epigrass Web password:")
    S = simulate(fname=args.epg[0], backend=args.backend)

    app_url = "http://app.epigrass.net/simulations/view/new/"  # creating the app id
    r = requests.get(app_url, auth=(username, passwd))
    fields = {'epg': (S.modelName, open(S.fname, 'rb'), 'text/plain')}
    if os.path.exists(os.path.join(S.outdir, 'data.json')):
        fields['map'] = ('data.json', open(os.path.join(S.outdir, 'data.json'), 'rb'), 'text/plain')
    if os.path.exists(os.path.join(S.outdir, 'series.json')):
        fields['series'] = ('series.json', open(os.path.join(S.outdir, 'series.json'), 'rb'), 'text/plain')
    if os.path.exists(os.path.join(S.outdir, 'network.json')):
        fields['network'] = ('network.json', open(os.path.join(S.outdir, 'network.json'), 'rb'), 'text/plain')
    if os.path.exists(os.path.join(S.outdir, 'spread.json')):
        fields['spread'] = ('spread.json', open(os.path.join(S.outdir, 'spread.json'), 'rb'), 'text/plain')

    hdrs = {'Content-Type': fields.content_type,
            'content-encoding': 'gzip',
            'transfer-encoding': 'chunked'}

    r = requests.post(app_url, files=fields, headers=hdrs)
    if r.status_code == requests.codes.ok:
        print "Model has been uploaded sucessfully!"
    else:
        print "Model Upload failed."


def main():
    # Options and Argument parsing for running model from the command line, without the GUI.
    usage = "usage: PROG [options] your_model.epg"
    #    parser = OptionParser(usage=usage, version="%prog "+__version__.version)
    parser = ArgumentParser(usage=usage, description="Run epigrass models from the console",
                            prog="epirunner " + __version__.version)
    parser.add_argument("-b", "--backend", dest="backend",
                        help="Define which datastorage backend to use", metavar="<mysql|sqlite|csv>", default="sqlite")
    parser.add_argument("-u", "--dbusername",
                        dest="dbuser", help="MySQL user name")
    parser.add_argument("-p", "--password",
                        dest="dbpass", help="MySQL password for user")
    parser.add_argument("-H", "--dbhost",
                        dest="dbhost", default="localhost", help="MySQL hostname or IP address")
    parser.add_argument("--upload", help="Upload your models and latest simulation to Epigrass Web")
    parser.add_argument("-P", "--parallel", action="store_true", default=False,
                        dest="parallel", help="use multiprocessing to run the simulation")
    parser.add_argument("epg", metavar='EPG', nargs=1,
                        help='Epigrass model definition file (.epg).')

    args = parser.parse_args()
    if args.backend == "mysql" and not (args.dbuser and args.dbpass):
        parser.error("You must specify a user and password when using MySQL.")
    if args.backend not in ['mysql', 'sqlite', 'csv']:
        parser.error('"%s" is an invalid backend type.' % args.backend)
    print
    '==> ', args.epg

    if args.upload:  # Only upload model
        upload_model(args)
    else:
        onStraightRun(args)


if __name__ == '__main__':
    main()
    




