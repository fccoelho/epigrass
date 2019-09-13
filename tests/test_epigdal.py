from __future__ import absolute_import
import unittest
from Epigrass.epigdal import World, KmlGenerator
import os


class TestWorld(unittest.TestCase):
    def test_instantiation(self):
        w = World('../riozonas_LatLong.shp', 'nome_zonas', 'zona_trafe')
        layer = w.ds.GetLayerByName(w.layerlist[0])
        w.get_node_list(layer)
        w.close_sources()
        self.assertIsInstance(w, World)
        self.assertGreater(len(w.nlist), 0)

    def test_create_node_layer(self):
        w = World('../riozonas_LatLong.shp', 'nome_zonas', 'zona_trafe')
        layer = w.ds.GetLayerByName(w.layerlist[0])
        w.get_node_list(layer)
        w.create_node_layer()
        w.close_sources()
        assert os.path.exists('Nodes.shp')
        assert os.path.exists('Nodes.prj')
        os.unlink('Nodes.shp')
        os.unlink('Nodes.shx')
        os.unlink('Nodes.dbf')
        os.unlink('Nodes.prj')

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
