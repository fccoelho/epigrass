import unittest
from Epigrass.manager import Simulate
import geopandas as gpd
import os
import pathlib

class SimulateTestCase(unittest.TestCase):
    def test_Instantiate(self):
        os.chdir(pathlib.Path(__file__).parent.absolute())
        S = Simulate(fname='SEIR.epg', backend='sqlite')
        self.assertIsInstance(S, Simulate)
        self.assertIsInstance(S.World.nodes, gpd.GeoDataFrame)


if __name__ == '__main__':
    unittest.main()
