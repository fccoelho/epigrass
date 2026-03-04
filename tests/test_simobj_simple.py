"""
Simple tests for simobj.py optimizations
Tests the core functionality without requiring full Epigrass dependencies
"""

import unittest
import sys
import os
import time
import numpy as np
import networkx as NX


# Test basic NetworkX integration
class TestNetworkXIntegration(unittest.TestCase):
    """Test NetworkX functions work correctly"""

    def test_networkx_available(self):
        """Verify NetworkX is available"""
        self.assertIsNotNone(NX)
        print(f"\n✅ NetworkX version: {NX.__version__}")

    def test_degree_function(self):
        """Test NetworkX degree function"""
        G = NX.MultiDiGraph()
        G.add_edge(1, 2)
        G.add_edge(1, 3)
        G.add_edge(2, 3)

        # Degree should be cached and fast
        degree = G.degree(1)
        self.assertEqual(degree, 2)  # 2 outgoing edges

        degree = G.degree(2)
        self.assertEqual(degree, 2)  # 1 in, 1 out

    def test_closeness_centrality(self):
        """Test NetworkX closeness centrality"""
        # Use undirected graph for simpler test
        G = NX.Graph()
        G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 5)])

        centrality = NX.closeness_centrality(G, 1)
        self.assertIsInstance(centrality, float)
        # Node 1 can reach all other nodes
        self.assertGreater(centrality, 0)
        self.assertLessEqual(centrality, 1)

        # Middle node should have higher centrality
        centrality_3 = NX.closeness_centrality(G, 3)
        self.assertGreater(centrality_3, centrality)

    def test_betweenness_centrality(self):
        """Test NetworkX betweenness centrality"""
        G = NX.DiGraph()
        G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 5)])

        betweenness = NX.betweenness_centrality(G, normalized=False, endpoints=False)
        self.assertIsInstance(betweenness, dict)

        # Node 3 should have highest betweenness (middle of chain)
        max_betweenness_node = max(betweenness, key=betweenness.get)
        self.assertIn(max_betweenness_node, [2, 3, 4])  # Middle nodes

    def test_shortest_path(self):
        """Test NetworkX shortest path"""
        G = NX.DiGraph()
        G.add_edges_from([(1, 2), (2, 3), (3, 4)])

        path = NX.shortest_path(G, 1, 4)
        self.assertEqual(path, [1, 2, 3, 4])

        # Test no path case
        G.add_node(5)  # Disconnected
        try:
            path = NX.shortest_path(G, 1, 5)
            self.fail("Should raise NetworkXNoPath")
        except NX.NetworkXNoPath:
            pass  # Expected

    def test_all_pairs_shortest_path_length(self):
        """Test NetworkX all pairs shortest path"""
        G = NX.DiGraph()
        G.add_edges_from([(1, 2), (2, 3), (3, 4)])

        lengths = dict(NX.all_pairs_shortest_path_length(G))

        self.assertIn(1, lengths)
        self.assertEqual(lengths[1][2], 1)
        self.assertEqual(lengths[1][3], 2)
        self.assertEqual(lengths[1][4], 3)


class TestPerformanceBenchmarks(unittest.TestCase):
    """Benchmark NetworkX performance"""

    def setUp(self):
        """Create test graphs of various sizes"""
        self.small_graph = NX.gnp_random_graph(10, 0.3, directed=True)
        self.medium_graph = NX.gnp_random_graph(100, 0.05, directed=True)
        self.large_graph = NX.gnp_random_graph(500, 0.01, directed=True)

    def test_degree_performance(self):
        """Benchmark degree computation"""
        print("\n" + "=" * 60)
        print("Degree Performance Benchmark")
        print("=" * 60)

        # Small graph
        start = time.time()
        for _ in range(1000):
            for node in self.small_graph.nodes():
                _ = self.small_graph.degree(node)
        small_time = time.time() - start
        print(f"Small graph (10 nodes, 1000 iterations): {small_time:.4f}s")

        # Medium graph
        start = time.time()
        for _ in range(100):
            for node in self.medium_graph.nodes():
                _ = self.medium_graph.degree(node)
        medium_time = time.time() - start
        print(f"Medium graph (100 nodes, 100 iterations): {medium_time:.4f}s")

        # Large graph
        start = time.time()
        for _ in range(10):
            for node in self.large_graph.nodes():
                _ = self.large_graph.degree(node)
        large_time = time.time() - start
        print(f"Large graph (500 nodes, 10 iterations): {large_time:.4f}s")

        # Degree should be very fast (O(1))
        self.assertLess(small_time, 0.1)
        self.assertLess(medium_time, 0.1)
        self.assertLess(large_time, 0.1)

    def test_centrality_performance(self):
        """Benchmark centrality computation"""
        print("\n" + "=" * 60)
        print("Centrality Performance Benchmark")
        print("=" * 60)

        # Small graph
        start = time.time()
        for node in self.small_graph.nodes():
            _ = NX.closeness_centrality(self.small_graph, node)
        small_time = time.time() - start
        print(f"Small graph (10 nodes): {small_time:.4f}s")

        # Medium graph
        start = time.time()
        for node in self.medium_graph.nodes():
            _ = NX.closeness_centrality(self.medium_graph, node)
        medium_time = time.time() - start
        print(f"Medium graph (100 nodes): {medium_time:.4f}s")

        # Should complete in reasonable time
        self.assertLess(small_time, 1.0)
        self.assertLess(medium_time, 10.0)

    def test_betweenness_performance(self):
        """Benchmark betweenness computation"""
        print("\n" + "=" * 60)
        print("Betweenness Performance Benchmark")
        print("=" * 60)

        # Small graph (exact)
        start = time.time()
        betweenness = NX.betweenness_centrality(self.small_graph, normalized=False)
        small_time = time.time() - start
        print(f"Small graph (10 nodes, exact): {small_time:.4f}s")

        # Medium graph (exact)
        start = time.time()
        betweenness = NX.betweenness_centrality(self.medium_graph, normalized=False)
        medium_time = time.time() - start
        print(f"Medium graph (100 nodes, exact): {medium_time:.4f}s")

        # Large graph (sampled)
        start = time.time()
        betweenness = NX.betweenness_centrality(
            self.large_graph, k=50, normalized=False
        )
        large_time = time.time() - start
        print(f"Large graph (500 nodes, sampled k=50): {large_time:.4f}s")

        # Should complete in reasonable time
        self.assertLess(small_time, 1.0)
        self.assertLess(medium_time, 10.0)
        self.assertLess(large_time, 10.0)

    def test_all_pairs_performance(self):
        """Benchmark all-pairs shortest path"""
        print("\n" + "=" * 60)
        print("All-Pairs Shortest Path Benchmark")
        print("=" * 60)

        # Small graph
        start = time.time()
        lengths = dict(NX.all_pairs_shortest_path_length(self.small_graph))
        small_time = time.time() - start
        print(f"Small graph (10 nodes): {small_time:.4f}s")

        # Medium graph
        start = time.time()
        lengths = dict(NX.all_pairs_shortest_path_length(self.medium_graph))
        medium_time = time.time() - start
        print(f"Medium graph (100 nodes): {medium_time:.4f}s")

        # Large graph
        start = time.time()
        lengths = dict(NX.all_pairs_shortest_path_length(self.large_graph))
        large_time = time.time() - start
        print(f"Large graph (500 nodes): {large_time:.4f}s")

        # Should complete in reasonable time
        self.assertLess(small_time, 1.0)
        self.assertLess(medium_time, 5.0)
        self.assertLess(large_time, 30.0)


class TestSimobjSyntax(unittest.TestCase):
    """Test that simobj.py has no syntax errors"""

    def test_syntax_check(self):
        """Verify simobj.py has no syntax errors"""
        import py_compile

        simobj_path = os.path.join(
            os.path.dirname(__file__), "..", "Epigrass", "simobj.py"
        )

        try:
            py_compile.compile(simobj_path, doraise=True)
            print("\n✅ simobj.py syntax check passed")
        except py_compile.PyCompileError as e:
            self.fail(f"Syntax error in simobj.py: {e}")

    def test_imports_available(self):
        """Test that required imports are available"""
        # These should always be available
        import numpy
        import networkx

        print(f"\n✅ numpy version: {numpy.__version__}")
        print(f"✅ networkx version: {networkx.__version__}")


def run_benchmarks():
    """Run performance benchmarks"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPerformanceBenchmarks)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
