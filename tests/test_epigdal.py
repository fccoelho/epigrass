from __future__ import absolute_import
import unittest
from Epigrass.epigdal import NewWorld as World, KmlGenerator
import os
import fiona
import pandas as pd


class TestWorld(unittest.TestCase):
    def test_instantiation(self):
        w = World('demos/riozonas_LatLong.shp', 'nome_zonas'.upper(), 'zona_trafe'.upper())

        self.assertIsInstance(w, World)
        self.assertGreater(len(w.map), 0)

    def test_get_layers(self):
        w = World('demos/riozonas_LatLong.shp', 'nome_zonas'.upper(), 'zona_trafe'.upper())
        layers = w.get_layer_list()
        self.assertIsInstance(layers, list)
        if len(layers):
            self.assertIsInstance(layers[0], str)

    def test_create_node_layer(self):
        w = World('demos/riozonas_LatLong.shp', 'nome_zonas'.upper(), 'zona_trafe'.upper())
        w.get_node_list()
        w.create_node_layer()
        self.assertIsInstance(w.nodesource, fiona.Collection)
        os.remove('Nodes.gpkg')

    def test_create_edge_layer(self):
        w = World('demos/riozonas_LatLong.shp', 'nome_zonas'.upper(), 'zona_trafe'.upper())
        w.get_node_list()
        cols = ['COD_ORIGEM', 'COD_DESTINO', 'flowOD', 'flowDO']
        edges = pd.read_csv('demos/edgesRIO.csv', usecols=cols)
        elist = edges[cols].values.tolist()
        w.create_edge_layer(elist)
        self.assertIsInstance(w.edgesource, fiona.Collection)
        os.remove('Edges.gpkg')

    def test_create_data_layer(self):
        w = World('demos/riozonas_LatLong.shp', 'nome_zonas'.upper(), 'zona_trafe'.upper())
        w.get_node_list()
        cols = ['COD_ORIGEM', 'COD_DESTINO', 'flowOD', 'flowDO']
        edges = pd.read_csv('demos/edgesRIO.csv', usecols=cols)
        elist = edges[cols].values.tolist()
        w.create_edge_layer(elist)
        self.assertIsInstance(w.edgesource, fiona.Collection)
        os.remove('Edges.gpkg')

    @unittest.skip
    def test_kml(self):
        w = World('demos/riozonas_LatLong.shp', 'nome_zonas'.upper(), 'zona_trafe'.upper())
        layer = w.ds.GetLayerByName(w.layerlist[0])
        w.get_node_list(layer)
        kmlg = KmlGenerator()
        kmlg.addNodes(layer)
        kmlg.writeToFile('.')


if __name__ == '__main__':
    unittest.main()
