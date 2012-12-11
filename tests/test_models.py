__author__ = 'fccoelho'


import unittest
from Epigrass.manager import *
from Epigrass.simobj import siteobj,graph,edge
from Epigrass.epimodels import Epimodel

class TestModels(unittest.TestCase):
    def setUp(self):
        pass

    def test_run_SIS(self):
        model = Epimodel("SIS")
        res = model.step((0,1,999),0,1000,0,0,bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'beta':0.01,'alpha':1.})
        self.assertAlmostEqual(res,([0,0.9,999.11],0,0.9))
        #TOdo: add asserts with the expected results of the models
    def test_run_SIS_s(self):
        model = Epimodel('SIS_s')
        res = model.step((0,1,999),0,1000,0,0,bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'beta':0.01,'alpha':1.})
        self.assertAlmostEqual(res,([0,0.9,999.11],0,0.9))
    def test_run_SIR(self):
        model = Epimodel('SIR')
        res = model.step((0,1,999),0,1000,0,0,bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'beta':0.01,'alpha':1.})
        self.assertAlmostEqual(res,([0,0.9,999.01],0,0.9))
    def test_run_SIR_s(self):
        model = Epimodel('SIR_s')
        res = model.step((0,1,999),0,1000,0,0,bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'beta':0.01,'alpha':1.})
    def test_run_SEIS(self):
        model = Epimodel('SEIS')
        res = model.step((0,1,999),0,1000,0,0,bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.1,'beta':0.01,'alpha':1.})
    def test_run_SEIS_s(self):
        model = Epimodel('SEIS_s')
        res = model.step((0,1,999),0,1000,0,0,bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.1,'beta':0.01,'alpha':1.})
    def test_run_SEIR(self):
        model = Epimodel('SEIR')
        res = model.step((0,1,999),0,1000,0,0,bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.1,'beta':0.01,'alpha':1.})
    def test_run_SEIR_s(self):
        model = Epimodel('SEIR_s')
        res = model.step((0,1,999),0,1000,0,0,bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.1,'beta':0.01,'alpha':1.})
    def test_run_SIpRpS(self):
        model = Epimodel('SIpRpS')
        res = model.step((0,1,999),0,1000,0,0,bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'beta':0.01,'alpha':1.,'delta':0.1})
    def test_run_Influenza(self):
        model = Epimodel('Influenza')
        res = model.step((999,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),0,1000,0,0,bi={'e1':0,'is1':1,'s1':999,'e2':0,'is2':1,'s2':0,'e3':0,'is3':1,'s3':0,'e4':0,'is4':1,'s4':0,'ic1':0,'ic2':0,'ic3':0,'ic4':0,'ig1':0,'ig2':0,'ig3':0,'ig4':0},bp={'r':0.1,'b':0.01,'beta':0.01,'e':0.1,'pc1':.1,'c':0.1,'pp1':.1,'g':.1,'d':.1,'pc2':.1,'pp2':.1,'pc3':.1,'pp3':.1,'pc4':.1,'pp4':.1,'alpha':1.,'delta':0.1,'vaccineNow':1,'vaccov':0.3})
    def test_run_SIpRpS_s(self):
        model = Epimodel('SIpRpS_s')
        res = model.step((0,1,999),0,1000,0,0,bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.1,'beta':0.01,'alpha':1.,'delta':0.1})
    def test_run_SEIpRpS(self):
        model = Epimodel('SEIpRpS')
        res = model.step((0,1,999),0,1000,0,0,bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.1,'beta':0.01,'alpha':1.,'delta':0.1})
    def test_run_SEIpRpS_s(self):
        model = Epimodel('SEIpRpS_s')
        res = model.step((0,1,999),0,1000,0,0,bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.1,'beta':0.01,'alpha':1.,'delta':0.1})
    def test_run_SIpR(self):
        model = Epimodel('SIpR')
        res = model.step((0,1,999),0,1000,0,0,bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'beta':0.01,'alpha':1.,'delta':0.1,'p':0.1})
    def test_run_SIpR_s(self):
        model = Epimodel('SIpR_s')
        res = model.step((0,1,999),0,1000,0,0,bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'beta':0.01,'alpha':1.,'delta':0.1,'p':0.1})
    def test_run_SEIpR(self):
        model = Epimodel('SEIpR')
        res = model.step((0,1,999),0,1000,0,0,bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.1,'beta':0.01,'alpha':1.,'delta':0.1,'p':0.1})
    def test_run_SEIpR_s(self):
        model = Epimodel('SEIpR_s')
        res = model.step((0,1,999),0,1000,0,0,bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'e':0.1,'beta':0.01,'alpha':1.,'delta':0.1,'p':0.1})
    def test_run_SIRS(self):
        model = Epimodel('SIRS')
        res = model.step((0,1,999),0,1000,0,0,bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'beta':0.01,'alpha':1.,'delta':0.1,'p':0.1,'w':0.1})
    def test_run_SIRS_s(self):
        model = Epimodel('SIRS_s')
        res = model.step((0,1,999),0,1000,0,0,bi={'e':0,'i':1,'s':999},bp={'r':0.1,'b':0.01,'beta':0.01,'alpha':1.,'delta':0.1,'p':0.1,'w':0.1})
