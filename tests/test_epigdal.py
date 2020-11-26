from __future__ import absolute_import
import unittest
from Epigrass.epigdal import NewWorld as World, KmlGenerator
import os



class TestWorld(unittest.TestCase):
    def test_instantiation(self):
        w = World('../riozonas_LatLong.shp', 'nome_zonas', 'zona_trafe')

        self.assertIsInstance(w, World)
        self.assertGreater(len(w.map), 0)

    def test_get_layers(self):
        w = World('../riozonas_LatLong.shp', 'nome_zonas', 'zona_trafe')
        layers = w.get_layer_list()
        self.assertIsInstance(layers, list)
        if len(layers):
            self.assertIsInstance(layers[0],str)

    def test_create_node_layer(self):
        pass


    @unittest.skip
    def test_kml(self):
        w = World('../riozonas_LatLong.shp', 'nome_zonas', 'zona_trafe')
        layer = w.ds.GetLayerByName(w.layerlist[0])
        w.get_node_list(layer)
        kmlg = KmlGenerator()
        kmlg.addNodes(layer)
        kmlg.writeToFile('.')


if __name__ == '__main__':
    unittest.main()
