#! /usr/bin/env python3
"""
Model Management and simulation objects.
"""
from __future__ import absolute_import
from __future__ import print_function
import time
from copy import deepcopy
from collections import OrderedDict
from argparse import ArgumentParser
from configparser import ConfigParser
import json
import sqlite3
import os
import getpass
from tqdm import tqdm
import pandas as pd
import pymysql.cursors
import numpy as np
from Epigrass.simobj import graph, edge, siteobj
from Epigrass import simobj
from Epigrass import spread
from Epigrass.data_io import *
from Epigrass import epigdal
from Epigrass import report
from Epigrass import __version__
import requests
import hashlib
import redis
import pickle
import multiprocessing


redisclient = redis.StrictRedis()


class Simulate:
    """
    This class takes care of setting up the model, simulating it, and storing the results
    """

    def __init__(self, fname=None, host='localhost', port=3306, db='epigrass', user='epigrass', password='epigrass',
                 backend='sqlite', silent=False):
        # pycallgraph.start_trace()
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
        sys.path.insert(0, self.dir)  # add current path to sys.path
        self.gui = 0  # True if this object was created by the gui
        self.now = time.asctime().replace(' ', '_').replace(':', '')  # current date and time
        self.modelName = os.path.split(self.fname)[-1].split('.')[0]
        self.config = self.loadModelScript(self.fname)
        self.evalConfig(self.config)
        if not self.outdir:
            self.outdir = outdir = 'outdata-' + self.modelName
        if not os.path.exists(self.outdir):
            os.mkdir(self.outdir)
        if self.shapefile:  # create world object if a shapefile is provided
            self.World = epigdal.NewWorld(*self.shapefile + [self.outdir])
        self.chkScript()
        self.encoding = 'utf-8'  # default encoding for strings in the sites and edges files
        self.round = 0  # No replicates
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
        cp = ConfigParser()
        cp.read(fname)
        for sec in cp.sections():
            name = sec.lower()
            for opt in cp.options(sec):
                config[name + "." + opt.lower()] = cp.get(sec, opt).strip()
        return config

    def evalConfig(self, config):
        """
        Takes in the config dictionary and generates the global variables needed.
        """
        try:
            # WORLD
            # load Shapefile if specified
            if config.get('the world.shapefile', False):
                self.shapefile = eval(config['the world.shapefile'])
            else:
                self.shapefile = []

            # self.layer = config['the world.vector layer']
            self.sites = config['the world.sites']  # file containing site info
            self.edges = config['the world.edges']  # file containing edge info
            if config['the world.encoding']:
                self.encoding = config['the world.encoding']  # encoding specification
            # Epidemiological model
            self.modtype = config['epidemiological model.modtype']
            # self.models = eval(config['epidemiological model.models'])
            # PARAMETERS
            self.beta = config['model parameters.beta']
            self.alpha = config['model parameters.alpha']
            self.e = config['model parameters.e']
            self.r = config['model parameters.r']
            self.delta = config['model parameters.delta']
            self.B = config['model parameters.b']
            self.w = config['model parameters.w']
            self.p = config['model parameters.p']
            # INITIAL CONDITIONS  (inits are string to evaluated inside siteobj.createmodel)
            # self.S = config['initial conditions.s']
            # self.E = config['initial conditions.e']
            # self.I = config['initial conditions.i']
            # EPIDEMIC EVENTS
            self.seed = eval(config['epidemic events.seed'])
            self.vaccinate = eval(config['epidemic events.vaccinate'])
            # self.quarantine = eval(config['epidemic events.quarantine'])

            # [TRANSPORTATION MODEL]
            self.doTransp = eval(config['transportation model.dotransp'])
            self.stochTransp = eval(config['transportation model.stochastic'])
            self.speed = eval(config['transportation model.speed'])

            # SIMULATION AND OUTPUT
            self.steps = eval(config['simulation and output.steps'])
            self.outdir = config['simulation and output.outdir']
            self.SQLout = eval(config['simulation and output.sqlout'])
            self.Rep = eval(config['simulation and output.report'])
            self.siteRep = eval(config['simulation and output.siterep'])
            self.replicas = eval(config['simulation and output.replicas'])
            self.randomize_seeds = eval(config['simulation and output.randseed'])
            self.Batch = eval(config['simulation and output.batch'])
        except KeyError as v:
            V = v.__str__().split('.')
            sys.exit("Please check the syntax of your '.epg' file.\nVariable %s, from section %s was not specified." % (
                V[1], V[0]))
        if self.replicas:
            self.Rep = 0  # Turns off reports
            self.Batch = []  # Turns off Batch mode
            self.round = 0  # Initialize replicate counter
            # generate dictionaries for parameters and inits
        self.inits = OrderedDict()
        self.parms = {}
        for k, v in config.items():
            try:
                k = k.decode('utf8')
            except AttributeError:
                pass
            if k.startswith('initial conditions'):
                self.inits[k.split('.')[-1].lower()] = v
            elif k.startswith('model parameters'):
                self.parms[k.split('.')[-1]] = v
            else:
                pass

    def chkScript(self):
        """
        Checks the type of the variables on the script
        """
        print("Checking syntax of model script... NOW")

        if not os.access(self.sites, os.F_OK):
            print('Sites file %s does not exist, please check your script.' % self.sites)
            sys.exit()
        if not os.access(self.edges, os.F_OK):
            print('Egdes file %s does not exist, please check your script.' % self.edges)
            sys.exit()
        if not self.modtype in ['SIS', 'SIS_s', 'SIR', 'SIR_s', 'SEIS', 'SEIS_s', 'SEIR', 'SEIR_s', 'SIpRpS',
                                'SIpRpS_s', 'SIpR,SIpR_s', 'Influenza', 'Custom']:
            print('Model type %s is invalid, please check your script.' % self.modtype)

        print('Script %s passed syntax check NOW.' % self.modelName)

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
            if ':' in str(site[0]):
                lat = self.deg2dec(str(site[0]))
                longit = self.deg2dec(str(site[1]))
            else:
                lat = site[0]
                longit = site[1]
            objlist.append(siteobj(site[2], site[3], (lat, longit), int((site[4])),
                                   tuple([float(i) for i in site[5:]])))
        for o in objlist:
            if self.stochTransp:
                o.stochtransp = 1
            else:
                o.stochtransp = 0
            N = o.totpop  # local copy for reference on model creation
            values = o.values  # local copy for reference on model creation
            inits = OrderedDict()
            parms = {}
            # eval parms and inits
            for k, v in self.inits.items():
                if isinstance(k, bytes):
                    k = k.decode('utf8')
                # inits[k.upper()] = eval(v)
                inits[k.lower()] = eval(v)
            for k, v in self.parms.items():
                if isinstance(k, bytes):
                    k = k.decode('utf8')
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
                # print type(o.geocode), type(self.seed[0])

                for j in self.seed:
                    if int(o.geocode) == j[0] or self.seed[0][0] == "all":
                        # print("%s infected person(s) arrived at %s"%(j[2],o.sitename))
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
        # print [i.sitename for i in sitelist]
        objlist = []
        source = dest = None
        for edg in edgelist:
            # print edgelist.index(edg)
            if edg[5] == edg[6]:
                # ignore circular edges
                continue
            for site in sitelist:
                # print site.sitename
                if site.geocode == edg[5]:
                    source = site
                    # print 'found source = ',source.sitename
                elif site.geocode == edg[6]:
                    dest = site
                    # print 'found dest = ',dest.sitename
                if (source and dest):
                    # print 'next edge!'
                    break
            if not (source and dest):
                print(type(edg[5]), type(edg[6]))
                sys.exit(
                    f'One of the vertices on edge {edg[0]}({edg[5]}) - {edg[1]}({edg[6]}) could not be found on the site list')

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
            poplist = [log10(site.totpop) for site in self.g.site_dict.values()]
            lpl = len(poplist)
            popprob = array(poplist) / sum(poplist)  # acceptance probability
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
        # inits[self.seed[0][1].lower()] += 1
        seedvar = self.seed[0][1].lower()  # retrieve the name of the variable containing the seeds
        print('seedvar= %s' % seedvar)
        site_list = self.g.site_list
        self.seed = [(seed.geocode, seedvar, n)]

        for site in site_list:
            if site.geocode == seed.geocode or seed.geocode == 'all':
                site.bi[seedvar] = n

                print("%s infected case(s) arrived at %s" % (n, seed.sitename))
            else:
                site.bi[seedvar] = 0

    def start(self):
        """
        Start the simulation
        """
        if '/' in self.modelName:
            self.modelName = os.path.split(self.modelName)[-1]
        #        print "====>", self.gui
        # time.sleep(10)
        print('Simulation starting.')
        start = time.time()
        self.runGraph(self.g, self.steps, transp=self.doTransp)
        elapsed = time.time() - start
        print('Simulation lasted %s seconds.' % elapsed)
        if self.SQLout:
            if self.backend == 'csv':
                self.outToCsv(self.modelName)
            else:
                self.outToDb(self.modelName)
        if self.shpout:
            self.outToShp()
        self.dumpData()
        spread.Spread(self.g, self.outdir, self.encoding)
        # self.saveModel(self.modelName)

    def createDataFrame(self, site):
        """
        Saves the time series *site.ts* to outfile as specified on the
        model script.
        """
        ts = array([eval(st) for st in redisclient.lrange(f'{site.geocode}:ts', 0, -1)])
        data = array(ts, float)
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

        return 'E,I,S\n'  # + tss

    def outToShp(self):
        """
        Creates Data Layers in shapefile format
        """
        if not self.World:
            return

        varlist = ["prevalence", "totalcases", "arrivals", "population"]
        sitestats = [(site.geocode, float(site.totalcases) / site.totpop, site.totalcases, sum(site.thetahist),
                      float(site.totpop)) for site in self.g.site_dict.values()]
        # simdf = pd.DataFrame(data=array(sitestats), columns=[self.World.geocfield] + varlist)
        # print(self.World.map.info())
        self.World.map[self.World.geocfield] = self.World.map[self.World.geocfield].astype(int)
        # self.World.map = pd.merge(self.World.map, simdf, on=self.World.geocfield)
        print('Saving results in the map Data.gpkg')
        self.World.create_data_layer(varlist, sitestats)

    def out_to_kml(self, names):
        """
        Generates output to kml files
        """
        print("Creating KML output files...")
        lr = self.World.datasource.GetLayer(0)
        k = epigdal.KmlGenerator()
        k.addNodes(lr, names)
        k.writeToFile(self.outdir)
        site_list = self.g.site_list
        site_dict = self.g.site_dict
        # Temporarily disabled animation output due to the sheer size of the kmz files
        if len(site_dict) * len(list(site_dict.values())[0].ts) < 20000:  # Only reasonably sized animations
            for i, v in enumerate(list(site_dict.values())[0].vnames):
                ka = epigdal.AnimatedKML(os.path.join(self.outdir, 'Data.kml'), extrude=True)
                data = []
                for site in site_dict.values():
                    ts = [eval(st) for st in redisclient.lrange(f'{site.geocode}:ts', 0, -1)]
                    for t, p in enumerate(ts):
                        data.append((str(site.geocode), t, p[i]))
                ka.add_data(data)
                ka.save(v + '_animation')
                print(v + '_animation')
                del ka
        else:
            print("Simulation too large to export as kml.")

        print("Done creating KML files!")

    def series_to_JSON(self):
        """
        Saves timeseries to JSON for uploading to epigrass web
        """
        print('Saving series to JSON')
        series = {}
        for gc, s in self.g.site_dict.items():
            length = max(map(len, s.ts))
            # y = np.array([xi + ([None] * (length - len(xi))) for xi in s.ts])
            y = np.array([np.pad(xi, length, 'constant', constant_values=np.NaN) for xi in s.ts])
            ts = np.array(y)
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
        cfgitems = list(self.config.items())
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
        tablee = table + "_" + self.now + "_e.csv.gz"  # edgetable name
        table += "_" + self.now + ".csv.gz"  # sitetable name

        head = ['geocode', 'time', 'totpop', 'name',
                'lat', 'longit']

        records = []
        for site in self.g.site_dict.values():
            t = 0
            regb = [str(site.geocode), str(t), str(site.totpop),
                    str(site.sitename).strip('"').encode('utf8', 'replace'),
                    str(site.pos[0]), str(site.pos[1])
                    ]
            if site.values:
                for n, v in enumerate(site.values):
                    regb.append(str(v))
            # print site.sitename, site.ts
            ts = array(site.ts[1:])  # remove init conds so that ts and inc are the same size
            # ts = array([eval(st) for st in redisclient.lrange(f'{site.geocode}:ts', 0, -1)])

            for i in ts:
                reg = deepcopy(regb)
                try:
                    reg.extend([str(site.incidence[t]), str(site.thetahist[t])])
                except IndexError:
                    print(len(site.incidence),len(site.thetahist),t)
                reg[1] = str(t)
                for n, v in enumerate(site.vnames):
                    reg.append(str(i[n]))
                records.append(reg)
                t += 1
        values = [f'value{n}' for n in range(len(site.values))]
        site_df = pd.DataFrame(columns=head+values+['incidence', 'arrivals']+site.vnames, data=records)
        site_df.to_csv(table)

        head = ['source_code', 'dest_code', 'time', 'ftheta', 'btheta']

        records = [[e.source.geocode, e.dest.geocode, t, f, b] for t, e in enumerate(self.g.edge_list) for f, b in zip(e.ftheta, e.btheta)]
        edge_df = pd.DataFrame(columns=head, data=records)

        edge_df.to_csv(tablee)

        os.chdir(self.dir)

    def writeMetaTable(self, table):
        """
        Creates a Meta-Info Table on the database with the contents of the .epg file
        """
        try:
            table = table + '_meta'
            if self.backend.lower() == "mysql":
                con = pymysql.connect(host=self.host, port=self.port,
                                      user=self.usr, passwd=self.passw, db=self.db)
            elif self.backend.lower() == "sqlite":
                if not self.outdir == os.getcwd():
                    os.chdir(self.outdir)
                con = sqlite3.connect("Epigrass.sqlite")
                os.chdir(self.dir)
            # Create table
            sqlstr1 = "CREATE TABLE %s(" % table
            vars = []
            cfgitems = list(self.config.items())
            for k, v in cfgitems:
                vars.append(k.strip().replace(' ', '_').replace('.', '$'))
            sqlstr2 = ', '.join(["%s text" % i for i in vars])
            Cursor = con.cursor()
            Cursor.execute(sqlstr1 + sqlstr2 + ');')
            # doing inserts
            values = [v.split('#')[0] for k, v in cfgitems]
            #            for k, v in cfgitems:
            #                v = v.split('#')[0]
            #                if not v:
            #                    v = ' '
            #                values.append()
            str3 = ','.join(['"%s"' % i for i in values]) + ')'
            sqlstr3 = '''INSERT INTO %s VALUES(%s''' % (table, str3)
            # print sqlstr3
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
            print('Saving data on MySQL...')
        elif self.backend.lower() == "sqlite":
            print('Saving data on SQLite...')

        con = None
        try:
            table = table + '_' + self.now
            self.writeMetaTable(table)
            self.outtable = table
            if self.backend.lower() == "mysql":
                con = pymysql.connect(host=self.host, port=self.port,
                                      user=self.usr, passwd=self.passw, db=self.db)
            elif self.backend.lower() == "sqlite":
                if not self.outdir == os.getcwd():
                    os.chdir(self.outdir)
                con = sqlite3.connect("Epigrass.sqlite")
                os.chdir(self.dir)
            # Define number of variables to be stored
            nvar = len(list(self.g.site_dict.values())[
                           0].vnames) + 4  # state variables,  plus coords, plus incidence, plus infected arrivals.
            str1 = '`%s` FLOAT(9),' * nvar  # nvar variables in the table
            str1lite = '%s REAL,' * nvar  # nvar variables in the SQLite table
            varnames = ['lat', 'longit'] + list(list(self.g.site_dict.values())[0].vnames) + ['incidence'] + [
                'Arrivals']
            #            print nvar, varnames, str1
            # print((nvar, len(varnames)))
            # print(varnames)
            str1 = str1[:-1] % tuple(varnames)  # insert variable names (MySQL)
            str1lite = str1lite[:len(str1lite) - 1] % tuple(varnames)  # insert variable names (SQLITE)
            Cursor = con.cursor()
            str2 = f"""CREATE TABLE {table}(
            `geocode` INT( 9 )  ,
            `time` INT( 9 ) ,
            `name` varchar(128) ,
            """
            str2lite = f"""CREATE TABLE {table}(
            geocode INTEGER,
            time INTEGER,
            name TEXT,
            """
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
            for site in self.g.site_dict.values():
                geoc = site.geocode
                lat = site.pos[0]
                longit = site.pos[1]
                name = site.sitename
                ts = array(site.ts[1:])  # remove init conds so that ts and inc are the same size
                # ts = array([eval(st) for st in redisclient.lrange(f'{geoc}:ts', 0, -1)])
                inc = site.incidence
                thist = site.thetahist
                t = 0
                for incid, flow in zip(inc, thist):
                    tstep = str(t)
                    flow = float(thist[t])
                    nvalues.append(tuple([geoc, tstep, name] + [lat, longit] + list(ts[t]) + [incid] + [flow]))
                    t += 1
            # print(nvalues[-1], len(ts[t]))
            Cursor.executemany(sql2, nvalues)
            con.commit()
            # Creating a table for edge data
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
            for gcs, e in self.g.edge_dict.items():
                s = gcs[0]
                d = gcs[1]
                t = 0
                for f, b in zip(e.ftheta, e.btheta):
                    values.append((s, d, t, f, b))
                    t += 1
            Cursor.executemany(esql2, values)


        finally:
            if con:
                con.commit()
                con.close()
        # saving pickle of adjacency matrix
        matname = 'adj_' + self.modelName  # table
        fname = os.path.join(self.outdir, matname)
        adjfile = open(fname, 'wb')
        pickle.dump(self.g.getConnMatrix(), adjfile)
        adjfile.close()

    def criaAdjMatrix(self):
        # saving the adjacency  matrix
        codeslist = [str(i.geocode) for i in self.g.site_dict.values()]
        if not os.path.exists('adjmat.csv'):
            print('Saving the adjacency  matrix...')
            am = self.g.getConnMatrix()
            amf = open('adjmat.csv', 'w')
            amf.write(','.join(codeslist) + '\n')
            for row in am:
                row = [str(i) for i in row]
                amf.write(','.join(row) + '\n')
            amf.close()
            print('Done!')

    def dumpData(self):
        """
        Dumps data as csv (comma-separated-values)
        """
        print("Starting simulation Analysis")
        curdir = os.getcwd()
        if not self.outdir == curdir:
            os.chdir(self.outdir)

        codeslist = list(self.g.site_dict.keys())
        self.criaAdjMatrix()
        # saving the shortest path matrices
        #        if not os.path.exists('spmat.csv'):
        #            print('Calculating the shortest path matrices...')
        #            ap = self.g.getAllPairs()
        #            f = open('ap','w')
        #            pickle.dump(ap,f)
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

        # Saving epidemic path
        print('Saving Epidemic path...')
        if self.round:
            epp = codecs.open('epipath%s.csv' % str(self.round), 'w', self.encoding)
        else:
            epp = codecs.open('epipath.csv', 'w', self.encoding)
        epp.write('time,site,infector\n')
        for i in self.g.epipath:
            # print i
            site = self.g.site_dict[i[1]]
            infectors = i[-1]
            # sorting infectors by number of infective contributed
            if len(infectors):
                reverse_infectors = list(infectors.items())
                reverse_infectors.sort(key=lambda t: t[1])
                mli = reverse_infectors[-1][0].sitename  # Most likely infector
            else:
                mli = 'NA'
            # print i[1].sitename, type(i[1].sitename), mli
            epp.write(f"{i[0]},{site.sitename},{mli}\n")
        epp.close()
        print('Done!')
        self.g.save_topology('network.gexf')

        # saving Epistats
        print('Saving Epidemiological results...')
        stats = [str(i) for i in self.g.getEpistats()]

        seed = \
            [s for s in self.g.site_dict.values() if s.geocode == self.seed[0][0] or self.seed[0][0] == 'all'][0]
        stats.pop(1)  # Remove epispeed which is a vector
        if os.path.exists('epistats.csv'):
            stf = codecs.open('epistats.csv', 'a', self.encoding)  # append to file
        else:
            stf = codecs.open('epistats.csv', 'w', self.encoding)  # create a new file
            stf.write(
                'seed,name,size,infected_sites,spreadtime,median_survival,totvaccinated,totquarantined,seeddeg,seedpop\n')
        ##            stf.write('seed,name,size,infected_sites,spreadtime,median_survival,totvaccinated,totquarantined,seeddeg,seedpop\n')
        # scent = str(seed.getCentrality())
        # sbetw = str(seed.getBetweeness())
        # sthidx = str(seed.getThetaindex())
        sdeg = str(seed.getDegree())
        spop = str(seed.totpop)
        sname = seed.sitename
        sstats = '%s,%s' % (sdeg, spop)
        #        sstats = '%s,%s,%s,%s,%s'%(scent,sbetw,sthidx,sdeg,spop)
        stf.write(str(self.seed[0][0]) + ',' + sname + ',' + ','.join(stats) + ',' + sstats + '\n')
        stf.close()
        print('Done saving!')

        # Saving site stats
        print('Saving site statistics...')
        # self.g.getAllPairs()
        if os.path.exists('sitestats.csv'):
            sitef = codecs.open('sitestats.csv', 'a', self.encoding)  # append to file
        else:
            sitef = codecs.open('sitestats.csv', 'w', self.encoding)

        # sitef.write('round,geocode,name,infection_time,degree,centrality,betweeness,theta_index,distance,seed,seedname\n')
        sitef.write('round,geocode,name,infection_time,degree,seed,seedname\n')
        for s in self.g.site_dict.values():
            degree = str(s.getDegree())
            # central = str(s.getCentrality())
            # bet = str(s.getBetweeness())
            # thidx = str(s.getThetaindex())
            seedgc = str(self.seed[0][0])
            seedname = seed.sitename
            #            f = open('ap','r')
            #            ap = pickle.load(f)
            #            f.close()
            #            distseed = str(ap[codeslist.index(str(s.geocode)),codeslist.index(str(self.seed[0][0]))])
            it = str(s.infected)  # infection time
            if it == 'FALSE':
                it = 'NA'

            #            sitef.write(str(self.round)+','+str(s.geocode)+','+s.sitename+','+it+','+degree+','+central+','+bet+','+thidx+','+distseed+','+seedgc+','+seedname+'\n')
            sitef.write(f"{self.round},{s.geocode} ,{s.sitename} ,{it}, {degree}, {seedgc}, {seedname}\n")

        # Saving series to JSON
        # self.series_to_JSON()
        os.chdir(curdir)

        print('Done saving data!')

    def saveModel(self, fname):
        """
        Save the fully specified graph.
        """
        f = open(fname, 'w')
        pickle.dump(self.g, f)
        f.close()

    def loadModel(self, fname):
        """
        Loads a pre-saved graph.
        """
        g = pickle.load(fname)
        return g

    def runGraph(self, graphobj, iterations=1, transp=1):
        """
        Starts the simulation on a graph.
        :param graphobj: The graph to run
        :param iterations: how many time steps to simulate
        :param transp: include the flow in the simulation
        """

        g = graphobj
        g.maxstep = iterations
        sites = list(graphobj.site_dict.values())
        edges = list(graphobj.edge_dict.values())
        # redisclient.flushall()
        if transp:
            for n in tqdm(range(iterations), desc='Simulation steps'):
                # print()
                # "==> {}\r".format(g.simstep),
                results = [i.runModel(self.parallel) for i in sites]
                if self.parallel:
                    [r.wait() for r in results]
                    # flows = PO.map(migrate, edges)
                    for j in edges:
                        j.migrate()
                else:
                    for j in edges:
                        j.migrate()

                g.simstep += 1
                g.sites_done = 0
        else:
            for n in tqdm(range(iterations), desc='Simulation steps'):
                results = []
                for i in tqdm(sites, desc='Sites'):
                    results.append(i.runModel(self.parallel))
                if self.parallel:
                    [r.wait() for r in results]

                g.simstep += 1

    def Say(self, string):
        """
        Exits outputs messages to the console or the gui accordingly
        """
        if self.silent:
            return
        print(string + '\r')


def migrate(edge):
    return edge.migrate()


def storeSimulation(S, usr, passw, db='epigrass', host='localhost', port=3306):
    """
    store the Simulate object *s* in the epigrass database
    to allow distributed runs. Currently not working.
    """
    now = time.asctime().replace(' ', '_').replace(':', '')
    table = 'Model_' + S.modelName + now
    con = pymysql.connect(host=host, port=port, user=usr, passwd=passw, db=db)
    Cursor = con.cursor()
    sql = """CREATE TABLE %s(
        `simulation` BLOB);""" % table
    Cursor.execute(sql)
    blob = pickle.dumps(S)
    sql2 = 'INSERT INTO %s' % table + ' VALUES(%s)'
    Cursor.execute(sql2, blob)
    con.close()


def onStraightRun(args):
    """
    Runs the model from the commandline
    """
    from Epigrass import epipanel
    if args.view_only:
        pth = os.path.join(os.getcwd() + f'/outdata-{args.epg[0].split(".")[0]}')
        os.chdir(os.path.abspath(pth))
        print(os.path.abspath(pth))
        epipanel.show(pth)
    redisclient.flushall()
    if args.backend == "mysql":
        S = Simulate(fname=args.epg[0], host=args.dbhost, user=args.dbuser, password=args.dbpass, backend=args.backend)
    else:
        S = Simulate(fname=args.epg[0], backend=args.backend)
    S.parallel = args.parallel
    if not S.replicas:
        S.start()
        spread.Spread(S.g)
        R = report.Report(S)
        R.Assemble(type=S.Rep)
    else:
        repRuns(S)
    if args.dashboard:
        epipanel.show(os.path.abspath(os.path.join(S.dir, S.outdir)))
    if S.Batch:
        S.Say('Simulation Started.')

        # run the batch list
        for i in S.Batch:
            # Makes sure it comes back to original directory before opening models in the batch list
            os.chdir(S.dir)
            # delete the old graph object to save memory
            S.graph = None
            # Generates the simulation object
            T = Simulate(fname=i, host=S.host, user=S.usr, password=S.passw, backend=S.backend)

            print('starting model %s' % i)
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
    nseeds = S.seed[0][2]  # number o individual to be used as seeds
    print("Replication type: ", randseed)
    if randseed:
        seeds = S.randomizeSeed(randseed)
    reps = S.replicas
    for i in range(reps):
        print("Starting replicate number %s" % i)
        S = Simulate(fname=fname, host=host, user=user, password=password, backend=backend)
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
    username = input("Enter your epigrass Web User id:")
    passwd = getpass("Enter your Epigrass Web password:")
    S = Simulate(fname=args.epg[0], backend=args.backend)

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
        print("Model has been uploaded sucessfully!")
    else:
        print("Model Upload failed.")


def main():
    # Options and Argument parsing for running model from the command line, without the GUI.
    usage = "usage: epirunner [options] your_model.epg"
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
    parser.add_argument("-D", "--dashboard", action="store_true", default=False,
                        dest="dashboard", help="Open dashboard on browser after th run is done.")
    parser.add_argument("-V", "--view-only", action="store_true", default=False,
                        dest="view_only", help="Only Open dashboard.")
    parser.add_argument("epg", metavar='EPG', nargs=1,
                        help='Epigrass model definition file (.epg).')

    args = parser.parse_args()
    if args.backend == "mysql" and not (args.dbuser and args.dbpass):
        parser.error("You must specify a user and password when using MySQL.")
    if args.backend not in ['mysql', 'sqlite', 'csv']:
        parser.error('"%s" is an invalid backend type.' % args.backend)
    print('==> ', args.epg)

    onStraightRun(args)


def end_pools():
    PO.close()
    PO.terminate()
    simobj.PO.close()
    simobj.PO.terminate()


PO = multiprocessing.Pool()
if __name__ == '__main__':
    import atexit

    atexit.register(end_pools)
    main()
