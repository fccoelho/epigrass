"""
Tests for basic simulation model objects instantiation
"""

from __future__ import absolute_import
import unittest
from Epigrass.manager import *
from Epigrass.simobj import siteobj, graph, edge
from Epigrass.report import Report


class testObjInstantiation(unittest.TestCase):
    def setUp(self):
        self.curdir = os.getcwd()
        os.chdir('./demos/')
        self.sitios = loadData('sitios3.csv', sep=',')
        self.edges = loadData('edgesout.csv', sep=',')
        self.S = Simulate('flu.epg')

    def tearDown(self):
        os.chdir(self.curdir)
        if os.path.exists('demos/outdata-flu'):
            os.system('rm -rf demos/outdata-flu')

    def testSites(self):
        l = self.S.instSites(self.sitios)
        for i in range(len(l)):
            self.assertEqual(l[i].sitename, self.sitios[i][2])

    def testEdges(self):
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        j = 0
        for i in e:
            self.assertEqual((i.source.geocode, i.dest.geocode), (int(self.edges[j][5]), int(self.edges[j][6])))
            j += 1

    def test_edge_migration(self):
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph('grafo', 1, l, e)
        g.simstep = 100
        for edge in e:
            edge.migrate()
            self.assertGreater(len(edge.dest.thetalist), 0)

    def testGraph(self):
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph('grafo', 1, l, e)
        self.assertEquals(len(g.site_dict), len(self.sitios))
        self.assertEquals(len(g.edge_dict), len(self.edges))

    def test_getAllPairs(self):
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph('grafo', 1, l, e)
        pairs = g.getAllPairs()

    def test_report(self):
        R = Report(self.S)
        src = R.Assemble(3, False)
        self.assertIn('Full Report', src)


class TestSimulationRuns(unittest.TestCase):
    def setUp(self):
        self.curdir = os.getcwd()
        os.chdir('demos/')
        #        self.sitios3 = loadData('sitios3.csv',sep=',')
        #        self.nodes = loadData('nodes.csv',sep=',')
        #        self.edgesout = loadData('edgesout.csv',sep=',')
        pass

    def test_mesh_epg(self):
        S = Simulate('mesh.epg', silent=True)
        S.start()

    def test_backend_csv(self):
        S = Simulate('mesh.epg', silent=True)
        S.backend = 'csv'
        S.start()

    def test_custom_model(self):
        S = Simulate('sars.epg', silent=True)
        S.start()

    def test_custom_model_parallel(self):
        S = Simulate('sars.epg', silent=True)
        S.parallel = True
        S.start()

    def tearDown(self):
        if os.path.exists('outdata-mesh'):
            os.system('rm -rf outdata-mesh')
        if os.path.exists('outdata-sars'):
            os.system('rm -rf outdata-sars')
        os.chdir('..')


if __name__ == '__main__':
    unittest.main()
