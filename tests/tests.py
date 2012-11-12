"""
Tests for basic simulation model objects instantiation
"""

import unittest
from Epigrass.manager import *
from Epigrass.simobj import siteobj,graph,edge

class testObjInstantiation(unittest.TestCase):
    def setUp(self):
        self.sitios = loadData('sitios3.csv',sep=',')
        self.ed=loadData('edgesout.csv',sep=',')
        self.S=simulate('flu.epg')
    def tearDown(self):
        if os.path.exists('demos/outdata-flu'):
            os.system('rm -rf demos/outdata-flu')

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
        self.assertEquals(len(g.site_dict), len(self.sitios))
        self.assertEquals(len(g.edge_dict),len(self.ed))

class TestModels(unittest.TestCase):
    def setUp(self):
        self.site = siteobj('teste',1000,(1.,1.),8716274)
        self.g = graph('teste',1)
        self.g.addSite(self.site)
    def test_run_SIS(self):
        self.site.createModel((0,1,999),'SIS',bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'beta':0.01,'alpha':1.})
        self.site.runModel()
        #TOdo: add asserts with the expected results of the models
    def test_run_SIS_s(self):
        self.site.createModel((0,1,999),'SIS_s',bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'beta':0.01,'alpha':1.})
        self.site.runModel()
    def test_run_SIR(self):
        self.site.createModel((0,1,999),'SIR',bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'beta':0.01,'alpha':1.})
        self.site.runModel()
    def test_run_SIR_s(self):
        self.site.createModel((0,1,999),'SIR_s',bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'beta':0.01,'alpha':1.})
        self.site.runModel()
    def test_run_SEIS(self):
        self.site.createModel((0,1,999),'SEIS',bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.01,'beta':0.01,'alpha':1.})
        self.site.runModel()
    def test_run_SEIS_s(self):
        self.site.createModel((0,1,999),'SEIS_s',bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.01,'beta':0.01,'alpha':1.})
        self.site.runModel()
    def test_run_SEIR(self):
        self.site.createModel((0,1,999),'SEIR',bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.01,'beta':0.01,'alpha':1.})
        self.site.runModel()
    def test_run_SEIR_s(self):
        self.site.createModel((0,1,999),'SEIR_s',bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.01,'beta':0.01,'alpha':1.})
        self.site.runModel()
    def test_run_SIpRpS(self):
        self.site.createModel((0,1,999),'SIpRpS',bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.01,'beta':0.01,'alpha':1.,'delta':0.1})
        self.site.runModel()
    def test_run_SIpRpS_s(self):
        self.site.createModel((0,1,999),'SIpRpS_s',bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.01,'beta':0.01,'alpha':1.,'delta':0.1})
        self.site.runModel()
    def test_run_SEIpRpS(self):
        self.site.createModel((0,1,999),'SEIpRpS',bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.01,'beta':0.01,'alpha':1.,'delta':0.1})
        self.site.runModel()
    def test_run_SEIpRpS_s(self):
        self.site.createModel((0,1,999),'SEIpRpS_s',bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.01,'beta':0.01,'alpha':1.,'delta':0.1})
        self.site.runModel()
    def test_run_SIpR(self):
        self.site.createModel((0,1,999),'SIpR',bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.01,'beta':0.01,'alpha':1.,'delta':0.1,'p':0.1})
        self.site.runModel()
    def test_run_SIpR_s(self):
        self.site.createModel((0,1,999),'SIpR_s',bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.01,'beta':0.01,'alpha':1.,'delta':0.1,'p':0.1})
        self.site.runModel()
    def test_run_SEIpR(self):
        self.site.createModel((0,1,999),'SEIpR',bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.01,'beta':0.01,'alpha':1.,'delta':0.1,'p':0.1})
        self.site.runModel()
    def test_run_SEIpR_s(self):
        self.site.createModel((0,1,999),'SEIpR_s',bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.01,'beta':0.01,'alpha':1.,'delta':0.1,'p':0.1})
        self.site.runModel()
    def test_run_SIRS(self):
        self.site.createModel((0,1,999),'SIRS',bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.01,'beta':0.01,'alpha':1.,'delta':0.1,'p':0.1,'w':0.1})
        self.site.runModel()
    def test_run_SIRS_s(self):
        self.site.createModel((0,1,999),'SIRS_s',bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.01,'beta':0.01,'alpha':1.,'delta':0.1,'p':0.1,'w':0.1})
        self.site.runModel()



#class TestSimulationRuns(unittest.TestCase):
#    def setUp(self):
#        os.chdir('demos/')
##        self.sitios3 = loadData('sitios3.csv',sep=',')
##        self.nodes = loadData('nodes.csv',sep=',')
##        self.edgesout = loadData('edgesout.csv',sep=',')
#        pass
#
#    def test_mesh_epg(self):
#        S = simulate('mesh.epg',silent=True)
#        S.start()
#    def test_custom_model(self):
#        S = simulate('sars.epg',silent=True)
#        S.start()
#    def tearDown(self):
#        if os.path.exists('outdata-mesh'):
#            os.system('rm -rf outdata-mesh')
#        os.chdir('..')


if __name__ == '__main__':
    unittest.main()
