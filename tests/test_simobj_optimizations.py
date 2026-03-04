"""
Tests for simobj.py optimizations
Tests verify that optimizations maintain correctness while improving performance
"""

from __future__ import absolute_import
import unittest
import time
import numpy as np
import networkx as NX
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Epigrass.manager import Simulate
from Epigrass.simobj import siteobj, graph, edge
from Epigrass.data_io import loadData


class TestOptimizations(unittest.TestCase):
    """Test all optimized methods"""

    def setUp(self):
        self.curdir = os.getcwd()
        if self.curdir.endswith("epigrass"):
            self.demos_dir = os.path.dirname(os.path.abspath("demos/flu"))
        else:
            self.demos_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demos/flu"
            )
        os.chdir(self.demos_dir)
        self.sitios = loadData("sitios3.csv", sep=",")
        self.edges = loadData("edgesout.csv", sep=",")
        self.S = Simulate("flu.epg", silent=True)

    def tearDown(self):
        os.chdir(self.curdir)
        outdir = os.path.join(self.demos_dir, "outdata-flu")
        if os.path.exists(outdir):
            os.system(f"rm -rf {outdir}")

    def test_getDegree_optimized(self):
        """Test optimized degree calculation"""
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph("grafo", 1, l, e)

        for site in l:
            degree_custom = site.getDegree()
            degree_nx = g.degree(site)

            # Should match NetworkX
            self.assertEqual(degree_custom, degree_nx)
            self.assertGreaterEqual(degree_custom, 0)

            # Should be cached (call again)
            degree_cached = site.getDegree()
            self.assertEqual(degree_custom, degree_cached)

    def test_getDegree_non_node(self):
        """Test degree for site not in graph"""
        site = siteobj("test", 1000, (0, 0), 12345)
        degree = site.getDegree()
        self.assertEqual(degree, 0)

    def test_getNeighbors_optimized(self):
        """Test optimized neighbor calculation"""
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph("grafo", 1, l, e)

        for site in l:
            neighbors = site.getNeighbors()

            # Should return dict
            self.assertIsInstance(neighbors, dict)

            # Each neighbor should be a siteobj with distance
            for neighbor, distance in neighbors.items():
                self.assertIsInstance(neighbor, siteobj)
                self.assertIsInstance(distance, (int, float))
                self.assertGreaterEqual(distance, 0)

            # Verify consistency with NetworkX
            nx_neighbors = set(g.neighbors(site))
            custom_neighbors = set(neighbors.keys())
            self.assertEqual(custom_neighbors, nx_neighbors)

    def test_getNeighbors_non_node(self):
        """Test neighbors for site not in graph"""
        site = siteobj("test", 1000, (0, 0), 12345)
        neighbors = site.getNeighbors()
        self.assertEqual(neighbors, {})

    def test_getNeighbors_caching(self):
        """Test that neighbors are cached"""
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph("grafo", 1, l, e)

        site = l[0]
        neighbors1 = site.getNeighbors()
        neighbors2 = site.getNeighbors()

        # Should be same object (cached)
        self.assertIs(neighbors1, neighbors2)

    def test_getCentrality_optimized(self):
        """Test optimized centrality calculation"""
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph("grafo", 1, l, e)

        for site in l:
            centrality = site.getCentrality()

            # Should return float
            self.assertIsInstance(centrality, float)

            # Should be in [0, 1] range
            self.assertGreaterEqual(centrality, 0.0)
            self.assertLessEqual(centrality, 1.0)

            # Verify consistency with NetworkX
            nx_centrality = NX.closeness_centrality(g, site)
            self.assertAlmostEqual(centrality, nx_centrality, places=5)

    def test_getCentrality_caching(self):
        """Test that centrality is cached"""
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph("grafo", 1, l, e)

        site = l[0]
        centrality1 = site.getCentrality()
        centrality2 = site.getCentrality()

        # Should be same value (cached)
        self.assertEqual(centrality1, centrality2)

    def test_getBetweeness_fixed(self):
        """Test that betweenness calculation works (was broken before)"""
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph("grafo", 1, l, e)

        # Compute betweenness for all nodes
        for site in l:
            betweeness = site.getBetweeness()

            # Should be non-negative number
            self.assertIsInstance(betweeness, (int, float))
            self.assertGreaterEqual(betweeness, 0)

        # Verify consistency with NetworkX
        nx_betweenness = NX.betweenness_centrality(g, normalized=False, endpoints=False)

        for site in l:
            custom_val = site.getBetweeness()
            nx_val = nx_betweenness.get(site, 0)
            self.assertAlmostEqual(custom_val, nx_val, places=3)

    def test_getBetweeness_not_always_zero(self):
        """Test that betweenness is not always zero (old bug)"""
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph("grafo", 1, l, e)

        # Compute betweenness for all nodes
        betweenness_values = [site.getBetweeness() for site in l]

        # At least some nodes should have non-zero betweenness in a connected graph
        # (unless it's a very simple graph structure)
        # This test might fail for very simple graphs, but should pass for most real networks
        total_betweenness = sum(betweenness_values)

        # For our test graph, we expect some non-zero values
        # (This would have failed with the old implementation)
        self.assertGreater(
            total_betweenness,
            0,
            "Betweenness should not all be zero (was bug in old implementation)",
        )

    def test_getBetweeness_caching(self):
        """Test that betweenness is cached"""
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph("grafo", 1, l, e)

        site = l[0]
        betweeness1 = site.getBetweeness()
        betweeness2 = site.getBetweeness()

        # Should be same value (cached)
        self.assertEqual(betweeness1, betweeness2)

    def test_getPiIndex_fixed(self):
        """Test that Pi index calculation doesn't crash"""
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph("grafo", 1, l, e)

        # This used to crash with IndexError
        pi = g.getPiIndex()

        # Should return a valid float
        self.assertIsInstance(pi, float)
        self.assertGreaterEqual(pi, 0.0)

    def test_getPiIndex_caching(self):
        """Test that Pi index is cached"""
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph("grafo", 1, l, e)

        pi1 = g.getPiIndex()
        pi2 = g.getPiIndex()

        # Should be same value (cached)
        self.assertEqual(pi1, pi2)

    def test_getAllPairs_optimized(self):
        """Test optimized all-pairs shortest path"""
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph("grafo", 1, l, e)

        # Get topological distance matrix
        ap = g.getAllPairs()

        # Should be numpy array
        self.assertIsInstance(ap, np.ndarray)

        # Should be square
        n = len(g.site_dict)
        self.assertEqual(ap.shape, (n, n))

        # Diagonal should be 0
        for i in range(n):
            self.assertEqual(ap[i, i], 0)

        # Should be cached
        ap2 = g.getAllPairs()
        self.assertTrue(np.array_equal(ap, ap2))

    def test_doStats_integration(self):
        """Test that doStats works with all optimizations"""
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph("grafo", 1, l, e)

        # This should not crash
        stats = g.doStats()

        # Should return list of stats
        self.assertIsInstance(stats, list)
        self.assertGreater(len(stats), 0)

        # All nodes should have computed centralities
        for site in l:
            self.assertIsNotNone(site.centrality)
            self.assertIsNotNone(site.betweeness)


class TestPerformance(unittest.TestCase):
    """Benchmark performance improvements"""

    def setUp(self):
        self.curdir = os.getcwd()
        self.demos_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demos", "flu"
        )
        os.chdir(self.demos_dir)
        self.sitios = loadData("sitios3.csv", sep=",")
        self.edges = loadData("edgesout.csv", sep=",")
        self.S = Simulate("flu.epg", silent=True)

    def tearDown(self):
        os.chdir(self.curdir)

    def test_degree_performance(self):
        """Benchmark degree calculation speed"""
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph("grafo", 1, l, e)

        # Time the optimized version
        iterations = 100
        start = time.time()
        for _ in range(iterations):
            for site in l:
                _ = site.getDegree()
        elapsed = time.time() - start

        print(f"\nDegree calculation ({iterations} iterations): {elapsed:.4f}s")

        # Should be very fast (O(1) per call)
        self.assertLess(elapsed, 2.0, "Degree calculation should be fast (O(1))")

    def test_centrality_performance(self):
        """Benchmark centrality calculation"""
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph("grafo", 1, l, e)

        # Clear cache first
        for node in l:
            node.centrality = None

        start = time.time()
        for node in l:
            _ = node.getCentrality()
        elapsed = time.time() - start

        print(f"\nCentrality calculation (individual): {elapsed:.4f}s")

        # Should complete in reasonable time
        self.assertLess(elapsed, 10.0, "Centrality calculation should complete")

    def test_betweeness_performance(self):
        """Benchmark betweenness calculation"""
        l = self.S.instSites(self.sitios)
        e = self.S.instEdges(l, self.edges)
        g = self.S.instGraph("grafo", 1, l, e)

        # Clear cache first
        for node in l:
            node.betweeness = None

        start = time.time()
        for node in l:
            _ = node.getBetweeness()
        elapsed = time.time() - start

        print(f"\nBetweenness calculation (individual): {elapsed:.4f}s")

        # Should complete in reasonable time
        self.assertLess(elapsed, 10.0, "Betweenness calculation should complete")


class TestBackwardCompatibility(unittest.TestCase):
    """Ensure optimizations don't break existing functionality"""

    def setUp(self):
        self.curdir = os.getcwd()
        self.demos_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demos"
        )
        os.chdir(self.demos_dir)

    def tearDown(self):
        os.chdir(self.curdir)
        # Clean up any output
        for model in ["mesh", "sars", "star"]:
            outdir = os.path.join(self.demos_dir, model, f"outdata-{model}")
            if os.path.exists(outdir):
                os.system(f"rm -rf {outdir}")

    def test_mesh_model_runs(self):
        """Test that mesh model still runs"""
        os.chdir(os.path.join(self.demos_dir, "mesh"))
        S = Simulate("mesh.epg", silent=True)
        S.start()
        # Should complete without errors

    def test_sars_model_runs(self):
        """Test that sars model still runs"""
        os.chdir(os.path.join(self.demos_dir, "sars"))
        S = Simulate("sars.epg", silent=True)
        S.start()
        # Should complete without errors

    def test_star_model_runs(self):
        """Test that star model still runs"""
        os.chdir(os.path.join(self.demos_dir, "star"))
        S = Simulate("star.epg", silent=True)
        S.start()
        # Should complete without errors


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def setUp(self):
        self.curdir = os.getcwd()
        self.demos_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demos"
        )
        # Don't load flu.epg for edge case tests - they create graphs manually

    def tearDown(self):
        os.chdir(self.curdir)

    def test_empty_graph(self):
        """Test methods on empty graph"""
        g = graph("empty")

        # Should handle empty graph gracefully
        self.assertEqual(len(g.site_dict), 0)
        self.assertEqual(len(g.edge_dict), 0)

    def test_single_node_graph(self):
        """Test methods on single-node graph"""
        g = graph("single")
        site = siteobj("test", 1000, (0, 0), 12345)
        g.addSite(site)

        # Degree should be 0
        self.assertEqual(site.getDegree(), 0)

        # Neighbors should be empty
        neighbors = site.getNeighbors()
        self.assertEqual(neighbors, {})

        # Centrality should be 0 (no other nodes)
        centrality = site.getCentrality()
        self.assertEqual(centrality, 0.0)

    def test_disconnected_graph(self):
        """Test methods on disconnected graph"""
        g = graph("disconnected")

        # Create two disconnected components
        site1 = siteobj("A", 1000, (0, 0), 1)
        site2 = siteobj("B", 1000, (1, 1), 2)
        site3 = siteobj("C", 1000, (2, 2), 3)
        site4 = siteobj("D", 1000, (3, 3), 4)

        g.addSite(site1)
        g.addSite(site2)
        g.addSite(site3)
        g.addSite(site4)

        # Connect A-B and C-D (two disconnected components)
        e1 = edge(site1, site2, 10, 10, 100)
        e2 = edge(site3, site4, 10, 10, 100)
        g.addEdge(e1)
        g.addEdge(e2)

        # Centrality should handle disconnected components
        centrality = site1.getCentrality()
        self.assertIsInstance(centrality, float)

        # Betweenness should work
        betweeness = site1.getBetweeness()
        self.assertIsInstance(betweeness, (int, float))


if __name__ == "__main__":
    # Run tests with verbosity
    unittest.main(verbosity=2)
