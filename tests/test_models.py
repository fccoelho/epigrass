from __future__ import absolute_import
from __future__ import print_function
from six.moves import zip
__author__ = 'fccoelho'

import unittest
from Epigrass.manager import *
from Epigrass.simobj import siteobj, graph, edge
from Epigrass.epimodels import Epimodel


class TestModels(unittest.TestCase):
    def setUp(self):
        pass

    def test_run_SIS(self):
        model = Epimodel(1, modtype="SIS")
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'beta': 0.01, 'alpha': 1.})
        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)
        #TOdo: add asserts with the expected results of the models

    def test_run_SIS_s(self):
        model = Epimodel(1, modtype='SIS_s')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'beta': 0.01, 'alpha': 1.})
        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SIR(self):
        model = Epimodel(1, modtype='SIR')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'beta': 0.01, 'alpha': 1.})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 1)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SIR_s(self):
        model = Epimodel(1, modtype='SIR_s')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'beta': 0.01, 'alpha': 1.})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 1)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SEIS(self):
        model = Epimodel(1, modtype='SEIS')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1.})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SEIS_s(self):
        model = Epimodel(1, modtype='SEIS_s')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1.})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SEIR(self):
        model = Epimodel(1, modtype='SEIR')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1.})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SEIR_s(self):
        model = Epimodel(1, modtype='SEIR_s')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1.})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SIpRpS(self):
        model = Epimodel(1, modtype='SIpRpS')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'beta': 0.01, 'alpha': 1., 'delta': 0.1})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_Influenza(self):
        model = Epimodel(1, modtype='Influenza')
        res = model.step((999, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), 0, 1000, 0, 0,
                         bi={'e1': 0, 'is1': 1, 's1': 999, 'e2': 0, 'is2': 1, 's2': 0, 'e3': 0, 'is3': 1, 's3': 0,
                             'e4': 0, 'is4': 1, 's4': 0, 'ic1': 0, 'ic2': 0, 'ic3': 0, 'ic4': 0, 'ig1': 0, 'ig2': 0,
                             'ig3': 0, 'ig4': 0},
                         bp={'r': 0.1, 'b': 0.01, 'beta': 0.01, 'e': 0.1, 'pc1': .1, 'c': 0.1, 'pp1': .1, 'g': .1,
                             'd': .1, 'pc2': .1, 'pp2': .1, 'pc3': .1, 'pp3': .1, 'pc4': .1, 'pp4': .1, 'alpha': 1.,
                             'delta': 0.1, 'vaccineNow': 1, 'vaccov': 0.3})
        # print res

        for x, y in zip(res[0], [699.3065035, 0.0034964999999999996, 0.9, 0.010000000000000002, 0.0, 0.01, 0.0, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.0]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0.003496, 3)
        self.assertAlmostEqual(res[2], 0.46, 2)

    def test_run_SIpRpS_s(self):
        model = Epimodel(1, modtype='SIpRpS_s')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1., 'delta': 0.1})

        # print res
        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SEIpRpS(self):
        model = Epimodel(1, modtype='SEIpRpS')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1., 'delta': 0.1})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SEIpRpS_s(self):
        model = Epimodel(1, modtype='SEIpRpS_s')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1., 'delta': 0.1})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SIpR(self):
        model = Epimodel(1, modtype='SIpR')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'beta': 0.01, 'alpha': 1., 'delta': 0.1, 'p': 0.1})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SIpR_s(self):
        model = Epimodel(1, modtype='SIpR_s')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'beta': 0.01, 'alpha': 1., 'delta': 0.1, 'p': 0.1})

        for x, y in zip(res[0], [0, 0.9, 999]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SEIpR(self):
        model = Epimodel(1, modtype='SEIpR')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1., 'delta': 0.1, 'p': 0.1})

        for x, y in zip(res[0], [0, 0.9, 999]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SEIpR_s(self):
        model = Epimodel(1, modtype='SEIpR_s')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1., 'delta': 0.1, 'p': 0.1})

        for x, y in zip(res[0], [0, 0.9, 999]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SIRS(self):
        model = Epimodel(1, modtype='SIRS')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'beta': 0.01, 'alpha': 1., 'delta': 0.1, 'p': 0.1, 'w': 0.1})
        print(res)
        for x, y in zip(res[0], [0, 0.9, 999]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SIRS_s(self):
        model = Epimodel(1, modtype='SIRS_s')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'beta': 0.01, 'alpha': 1., 'delta': 0.1, 'p': 0.1, 'w': 0.1})
        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)