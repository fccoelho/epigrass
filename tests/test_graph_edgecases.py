"""Edge-case tests for graph/site methods (salvaged from the retired
test_simobj_optimizations.py, which hung on its performance benchmarks)."""

import unittest

from Epigrass.simobj import edge, graph, siteobj


class TestGraphEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

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

        # Sites should recognize their graph membership
        for site in (site1, site2, site3, site4):
            self.assertTrue(site.isNode())

        # Degree: one edge per site in this configuration
        self.assertEqual(site1.getDegree(), 1)
        self.assertEqual(site3.getDegree(), 1)


if __name__ == "__main__":
    unittest.main()
