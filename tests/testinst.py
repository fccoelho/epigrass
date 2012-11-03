"""
Tests for basic simulation model objects instantiation
"""

import unittest
from Epigrass.manager import *
class testObjInstantiation(unittest.TestCase):
    def setUp(self):
        self.sitios = loadData('sitios3.csv',sep=',')
        self.ed=loadData('edgesout.csv',sep=',')
        self.S=simulate('flu.epg')
    def tearDown(self):
        if os.path.exists('demos/outdata-flu'):
            os.rmdir('demos/outdata-flu')

    def testSites(self):
        l = self.S.instSites(self.sitios)
        for i in range(len(l)):
            self.assertEqual(l[i].sitename,self.sitios[i][2])
            
    def testEdges(self):
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l,self.ed)
        j = 0
        for i in e:
            self.assertEqual((i.source.geocode, i.dest.geocode),(int(self.ed[j][5]),int(self.ed[j][6])))
            j+=1
    def testGraph(self):
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l,self.ed)
        g = self.S.instGraph('grafo',1,l,e)
        self.assertEquals(len(g.site_list), len(self.sitios))
        self.assertEquals(len(g.edge_list),len(self.ed))

class TestSimulationRuns(unittest.TestCase):
    def setUp(self):
        os.chdir('demos/')
#        self.sitios3 = loadData('sitios3.csv',sep=',')
#        self.nodes = loadData('nodes.csv',sep=',')
#        self.edgesout = loadData('edgesout.csv',sep=',')
        pass

    def test_mesh_epg(self):
        S = simulate('mesh.epg',silent=True)
        S.start()
    def tearDown(self):
        if os.path.exists('outdata-mesh'):
            os.system('rm -rf outdata-mesh')
        os.chdir('..')


if __name__ == '__main__':
    unittest.main()
