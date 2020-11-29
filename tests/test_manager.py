import unittest
from Epigrass.manager import Simulate
import geopandas as gpd

class SimulateTestCase(unittest.TestCase):
    def test_Instantiate(self):
        S = Simulate(fname='SEIR.epg', backend='sqlite')
        self.assertIsInstance(S, Simulate)
        self.assertIsInstance(S.World.nodes, gpd.GeoDataFrame)


if __name__ == '__main__':
    unittest.main()
