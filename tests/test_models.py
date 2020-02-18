from __future__ import absolute_import
from __future__ import print_function
from six.moves import zip
__author__ = 'fccoelho'

import unittest
# from Epigrass.manager import *
from Epigrass.simobj import siteobj, graph, edge
from Epigrass.epimodels import Epimodel


class TestModels(unittest.TestCase):
    def setUp(self):
        pass

    def test_run_SIS(self):
        model = Epimodel(1, modtype=b"SIS")
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'beta': 0.01, 'alpha': 1.})
        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)
        #TOdo: add asserts with the expected results of the models

    def test_run_SIS_s(self):
        model = Epimodel(1, modtype=b'SIS_s')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'beta': 0.01, 'alpha': 1.})
        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SIR(self):
        model = Epimodel(1, modtype=b'SIR')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={b'e': 0, b'i': 1, b's': 999},
                         bp={b'r': 0.1, b'b': 0.01, b'beta': 0.01, b'alpha': 1.})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 1)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SIR_s(self):
        model = Epimodel(1, modtype=b'SIR_s')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'beta': 0.01, 'alpha': 1.})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 1)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SEIS(self):
        model = Epimodel(1, modtype=b'SEIS')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1.})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SEIS_s(self):
        model = Epimodel(1, modtype=b'SEIS_s')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1.})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SEIR(self):
        model = Epimodel(1, modtype=b'SEIR')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1.})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SEIR_s(self):
        model = Epimodel(1, modtype=b'SEIR_s')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1.})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SIpRpS(self):
        model = Epimodel(1, modtype=b'SIpRpS')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'beta': 0.01, 'alpha': 1., 'delta': 0.1})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    # def test_run_Influenza(self):
    #     model = Epimodel(1, modtype=b'Influenza')
    #     res = model.step((999, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), 0, 1000, 0, 0,
    #                      bi={b'e1': 0, b'is1': 1, b's1': 999, b'e2': 0, b'is2': 1, b's2': 0, b'e3': 0, b'is3': 1, b's3': 0,
    #                          b'e4': 0, b'is4': 1, b's4': 0, b'ic1': 0, b'ic2': 0, b'ic3': 0, b'ic4': 0, b'ig1': 0, b'ig2': 0,
    #                          b'ig3': 0, b'ig4': 0},
    #                      bp={b'r': 0.1, b'b': 0.01, b'beta': 0.01, b'e': 0.1, b'pc1': .1, b'c': 0.1, b'pp1': .1, b'g': .1,
    #                          b'd': .1, b'pc2': .1, b'pp2': .1, b'pc3': .1, b'pp3': .1, b'pc4': .1, b'pp4': .1, b'alpha': 1.,
    #                          b'delta': 0.1, b'vaccineNow': 1, b'vaccov': 0.3})
    #     # print res

        # for x, y in zip(res[0], [999.3065035, 0.0049949993999999996, 0.9, 0.010000000000000002, 0.0, 0.01, 0.0, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.0]):
        #     self.assertAlmostEqual(x, y, 0)
        # self.assertAlmostEqual(res[1], 0.003496, 3)
        # self.assertAlmostEqual(res[2], 0.46, 2)

    def test_run_SIpRpS_s(self):
        model = Epimodel(1, modtype=b'SIpRpS_s')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1., 'delta': 0.1})

        # print res
        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SEIpRpS(self):
        model = Epimodel(1, modtype=b'SEIpRpS')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1., 'delta': 0.1})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SEIpRpS_s(self):
        model = Epimodel(1, modtype=b'SEIpRpS_s')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1., 'delta': 0.1})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SIpR(self):
        model = Epimodel(1, modtype=b'SIpR')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'beta': 0.01, 'alpha': 1., 'delta': 0.1, 'p': 0.1})

        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SIpR_s(self):
        model = Epimodel(1, modtype=b'SIpR_s')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'beta': 0.01, 'alpha': 1., 'delta': 0.1, 'p': 0.1})

        for x, y in zip(res[0], [0, 0.9, 999]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SEIpR(self):
        model = Epimodel(1, modtype=b'SEIpR')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1., 'delta': 0.1, 'p': 0.1})

        for x, y in zip(res[0], [0, 0.9, 999]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SEIpR_s(self):
        model = Epimodel(1, modtype=b'SEIpR_s')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1., 'delta': 0.1, 'p': 0.1})

        for x, y in zip(res[0], [0, 0.9, 999]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SIRS(self):
        model = Epimodel(1, modtype=b'SIRS')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'beta': 0.01, 'alpha': 1., 'delta': 0.1, 'p': 0.1, 'w': 0.1})
        print(res)
        for x, y in zip(res[0], [0, 0.9, 999]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)

    def test_run_SIRS_s(self):
        model = Epimodel(1, modtype=b'SIRS_s')
        res = model.step((0, 1, 999), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'beta': 0.01, 'alpha': 1., 'delta': 0.1, 'p': 0.1, 'w': 0.1})
        for x, y in zip(res[0], [0, 0.9, 999.01]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 0.9, 1)