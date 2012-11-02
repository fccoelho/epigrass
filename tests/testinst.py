"""
Unit testing script
"""

import unittest
from Epigrass.manager import *
class testObjInstantiation(unittest.TestCase):
    def setUp(self):
        self.sitios = loadData('sitios3.csv',sep=',')
        self.ed=loadData('edgesout.csv',sep=',')
        self.S=simulate('flu.epg')
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
        
        print g, g.getSiteNames()
if __name__ == '__main__':
    unittest.main()
