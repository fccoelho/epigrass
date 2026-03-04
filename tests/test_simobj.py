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
        self.demos_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demos", "flu"
        )
        os.chdir(self.demos_dir)
        self.sitios = loadData("sitios3.csv", sep=",")
        self.edges = loadData("edgesout.csv", sep=",")
        self.S = Simulate("flu.epg")

    def tearDown(self):
        os.chdir(self.curdir)
        outdir = os.path.join(self.demos_dir, "outdata-flu")
        if os.path.exists(outdir):
            os.system(f"rm -rf {outdir}")

    def testSites(self):
        l = self.S.instSites(self.sitios)
        for i in range(len(l)):
            self.assertEqual(l[i].sitename, self.sitios[i][2])

    def testEdges(self):
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        j = 0
        for i in e:
            self.assertEqual(
                (i.source.geocode, i.dest.geocode),
                (int(self.edges[j][5]), int(self.edges[j][6])),
            )
            j += 1

    def test_edge_migration(self):
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph("grafo", 1, l, e)
        g.simstep = 100
        for edge in e:
            edge.migrate()
            self.assertGreater(len(edge.dest.thetalist), 0)

    def testGraph(self):
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph("grafo", 1, l, e)
        self.assertEqual(len(g.site_dict), len(self.sitios))
        self.assertEqual(len(g.edge_dict), len(self.edges))

    def test_getAllPairs(self):
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph("grafo", 1, l, e)
        pairs = g.getAllPairs()

    def test_report(self):
        R = Report(self.S)
        src = R.Assemble(3, False)
        self.assertIn("Full Report", src)


class TestSimulationRuns(unittest.TestCase):
    def setUp(self):
        self.curdir = os.getcwd()
        self.demos_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demos"
        )

    def test_mesh_epg(self):
        os.chdir(os.path.join(self.demos_dir, "mesh"))
        S = Simulate("mesh.epg", silent=True)
        S.start()

    def test_backend_csv(self):
        os.chdir(os.path.join(self.demos_dir, "mesh"))
        S = Simulate("mesh.epg", silent=True)
        S.backend = "csv"
        S.start()

    def test_custom_model(self):
        os.chdir(os.path.join(self.demos_dir, "sars"))
        S = Simulate("sars.epg", silent=True)
        S.start()

    def test_custom_model_parallel(self):
        os.chdir(os.path.join(self.demos_dir, "sars"))
        S = Simulate("sars.epg", silent=True)
        S.parallel = True
        S.start()

    def tearDown(self):
        for model in ["mesh", "sars"]:
            outdir = os.path.join(self.demos_dir, model, f"outdata-{model}")
            if os.path.exists(outdir):
                os.system(f"rm -rf {outdir}")
        os.chdir(self.curdir)


if __name__ == "__main__":
    unittest.main()
