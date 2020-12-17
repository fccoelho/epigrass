from __future__ import absolute_import
from __future__ import print_function
from six.moves import zip

__author__ = 'fccoelho'

import unittest
import numpy as np
# from Epigrass.manager import *
from Epigrass.simobj import siteobj, graph, edge
from Epigrass.models import Epimodel


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

        # TOdo: add asserts with the expected results of the models

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
        res = model.step((0, 10, 990), 0, 1000, 0, 0, bi={'e': 0, 'i': 1, 's': 999},
                         bp={'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 0.01, 'alpha': 1., 'delta': 0.1, 'p': 0.1})

        for x, y in zip(res[0], [0, 9, 990]):
            self.assertAlmostEqual(x, y, 0)
        self.assertAlmostEqual(res[1], 0, 1)
        self.assertAlmostEqual(res[2], 9, 1)

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


import pylab as P


def run(model, args, n):
    res = []
    for i in range(n):
        args[1] = i
        out = model.step(*tuple(args))
        res.append(
            out[0]
        )
        args[0] = out[0]
    return np.array(res)


class test_model_run(unittest.TestCase):
    def setUp(self):
        self.bi = {'e': 0, 'i': 10, 's': 9999}
        self.bp = {'r': 0.1, 'b': 0.01, 'e': 0.1, 'beta': 1, 'alpha': 1., 'delta': 0.1, 'p': 0.1, 'w': 0.1}

    def tearDown(self):
        P.show()

    def test_run_SIRS_s(self):
        model = Epimodel(1, modtype=b'SIRS_s')
        res = run(model, [(0, 10, 999), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SIRS_s$')
        P.legend(['E', 'I', 'S'])

    def test_run_SIRS(self):
        model = Epimodel(1, modtype=b'SIRS')
        res = run(model, [(0, 1, 999), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SIRS$')
        P.legend(['E', 'I', 'S'])

    def test_run_SEIpR_s(self):
        model = Epimodel(1, modtype=b'SEIpR_s')
        res = run(model, [(0, 10, 990), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SEIpR_s$')
        P.legend(['E', 'I', 'S'])

    def test_run_SEIpR(self):
        model = Epimodel(1, modtype=b'SEIpR')
        res = run(model, [(0, 10, 990), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SEIpR$')
        P.legend(['E', 'I', 'S'])

    def test_run_SIpR_s(self):
        model = Epimodel(1, modtype=b'SIpR_s')
        res = run(model, [(0, 10, 990), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SIpR_s$')
        P.legend(['E', 'I', 'S'])

    def test_run_SIpR(self):
        model = Epimodel(1, modtype=b'SIpR')
        res = run(model, [(0, 10, 990), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SIpR$')
        P.legend(['E', 'I', 'S'])

    def test_run_SEIpRpS_s(self):
        model = Epimodel(1, modtype=b'SEIpRpS_s')
        res = run(model, [(0, 10, 990), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SEIpRpS_s$')
        P.legend(['E', 'I', 'S'])

    def test_run_SEIpRpS(self):
        model = Epimodel(1, modtype=b'SEIpRpS')
        res = run(model, [(0, 10, 990), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SEIpRpS$')
        P.legend(['E', 'I', 'S'])

    def test_run_SIpRpS_s(self):
        model = Epimodel(1, modtype=b'SIpRpS_s')
        res = run(model, [(0, 10, 990), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SIpRpS_s$')
        P.legend(['E', 'I', 'S'])

    def test_run_SIpRpS(self):
        model = Epimodel(1, modtype=b'SIpRpS')
        res = run(model, [(0, 10, 990), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SIpRpS$')
        P.legend(['E', 'I', 'S'])

    def test_run_SEIR_s(self):
        model = Epimodel(1, modtype=b'SEIR_s')
        res = run(model, [(0, 10, 990), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SEIR_s$')
        P.legend(['E', 'I', 'S'])

    def test_run_SEIR(self):
        model = Epimodel(1, modtype=b'SEIR')
        res = run(model, [(0, 10, 990), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SEIR$')
        P.legend(['E', 'I', 'S'])

    def test_run_SEIR_cont(self):
        model = Epimodel(1, modtype=b'SEIR_cont')
        res = run(model, [(0, 10, 990), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SEIR_{cont}$')
        P.legend(['E', 'I', 'S'])

    def test_run_SEIS_s(self):
        model = Epimodel(1, modtype=b'SEIS_s')
        res = run(model, [(0, 10, 990), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SEIS_s$')
        P.legend(['E', 'I', 'S'])

    def test_run_SEIS(self):
        model = Epimodel(1, modtype=b'SEIS')
        res = run(model, [(0, 10, 990), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SEIS$')
        P.legend(['E', 'I', 'S'])

    def test_run_SIR_s(self):
        model = Epimodel(1, modtype=b'SIR_s')
        res = run(model, [(0, 10, 990), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SIR_s$')
        P.legend(['E', 'I', 'S'])

    def test_run_SIR(self):
        model = Epimodel(1, modtype=b'SIR')
        res = run(model, [(0, 10, 990), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SIR$')
        P.legend(['E', 'I', 'S'])

    def test_run_SIR_cont(self):
        model = Epimodel(1, modtype=b'SIR_cont')
        res = run(model, [(0, 10, 990), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SIR_{cont}$')
        P.legend(['E', 'I', 'S'])

    def test_run_SIS_s(self):
        model = Epimodel(1, modtype=b'SIS_s')
        res = run(model, [(0, 10, 990), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SIS_s$')
        P.legend(['E', 'I', 'S'])

    def test_run_SIS(self):
        model = Epimodel(1, modtype=b'SIS')
        res = run(model, [(0, 10, 990), 0, 10000, 0, 0,
                          self.bi,
                          self.bp],
                  100)
        P.plot(res)
        P.title('$SIS$')
        P.legend(['E', 'I', 'S'])



    def test_run_Influenza(self):
        model = Epimodel(1, modtype=b'Influenza')
        res = run(model, [(2490, 0, 10, 0, 0, 2490, 0, 10, 0, 0, 2490, 0, 10, 0, 0, 2490, 0, 10, 0, 0), 0, 10000, 0, 0,
                          {b'incub_age1': 0, b'subc_age1': 10, b'susc_age1': 2490, b'incub_age2': 0, b'subc_age2': 10, b'susc_age2': 2490, b'incub_age3': 0, b'subc_age3': 10,
                           b'susc_age3': 2490,
                           b'incub_age4': 0, b'subc_age4': 10, b'susc_age4': 2490, b'sympt_age1': 0, b'sympt_age2': 0, b'sympt_age3': 0, b'sympt_age4': 0, b'comp_age1': 0,
                           b'comp_age2': 0,
                           b'comp_age3': 0, b'comp_age4': 0},
                          {b'r': 0.1, b'b': 0.01, b'beta': 1, b'e': 0.1, b'pc1': .1, b'c': 0.1, b'pp1': .1,
                           b'g': .1,
                           b'd': .1, b'pc2': .1, b'pp2': .1, b'pc3': .1, b'pp3': .1, b'pc4': .1, b'pp4': .1,
                           b'alpha': 1., b'delta': 0.1, b'vaccineNow': 1, b'vaccov': 0.3}], 100)
        P.plot(res)
        P.title('Influenza')
        P.legend(['Susc_age1', 'Incub_age1', 'Subc_age1', 'Sympt_age1', 'Comp_age1',
                  'Susc_age2', 'Incub_age2', 'Subc_age2', 'Sympt_age2', 'Comp_age2',
                  'Susc_age3', 'Incub_age3', 'Subc_age3', 'Sympt_age3', 'Comp_age3',
                  'Susc_age4', 'Incub_age4', 'Subc_age4', 'Sympt_age4', 'Comp_age4'])