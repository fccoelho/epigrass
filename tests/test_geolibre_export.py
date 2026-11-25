"""Tests for the GeoLibre project export (Epigrass.geolibre_export)."""

import json
import os
import sqlite3
import unittest

from Epigrass import geolibre_export


class TestGeoLibreExport(unittest.TestCase):
    """Exercise export_project against a synthetic Epigrass.sqlite."""

    def setUp(self):
        import tempfile

        self.outdir = tempfile.mkdtemp(prefix="outdata-test-")
        con = sqlite3.connect(os.path.join(self.outdir, "Epigrass.sqlite"))
        con.execute(
            "CREATE TABLE sim_Mon_Jan_01_000000_2026e "
            "(source_code, dest_code, time, ftheta, btheta)"
        )
        con.execute(
            "CREATE TABLE sim_Mon_Jan_01_000000_2026_meta (k, v)"
        )
        con.execute(
            "CREATE TABLE sim_Mon_Jan_01_000000_2026 "
            "(geocode, time, name, lat, longit, Exposed, Infectious, "
            "Susceptible, incidence)"
        )
        # Two sites, two steps; site 2 has a NULL (NaN) value on step 1.
        rows = [
            (1, 0, "Alpha", -10.0, -20.0, 0, 5, 95, 5),
            (1, 1, "Alpha", -10.0, -20.0, 2, 4, 94, 1),
            (2, 0, "Beta", -11.0, -21.0, 1, 1, 98, 1),
            (2, 1, "Beta", -11.0, -21.0, None, 2, 97, 1),
        ]
        con.executemany(
            "INSERT INTO sim_Mon_Jan_01_000000_2026 VALUES "
            "(?,?,?,?,?,?,?,?,?)",
            rows,
        )
        con.execute(
            "INSERT INTO sim_Mon_Jan_01_000000_2026_meta VALUES ('seed', '42')"
        )
        con.execute(
            "INSERT INTO sim_Mon_Jan_01_000000_2026e "
            "VALUES (1, 2, 0, 0.5, 0.1)"
        )
        con.commit()
        con.close()

    def test_export_writes_project(self):
        path = geolibre_export.export_project(self.outdir)
        self.assertTrue(os.path.exists(path))
        self.assertTrue(path.endswith(".geolibre.json"))
        with open(path, encoding="utf-8") as fobj:
            project = json.load(fobj)
        self.assertEqual(project["format"], "epigrass-geolibre-project")
        self.assertEqual(project["version"], 1)
        self.assertEqual(project["simulation"],
                         "sim_Mon_Jan_01_000000_2026")
        self.assertEqual(project["model"], "sim")
        self.assertEqual(len(project["sites"]), 2)
        self.assertEqual(project["times"], [0, 1])
        self.assertEqual(project["variables"],
                         ["Exposed", "Infectious", "Susceptible", "incidence"])
        alpha = project["series"]["1"]
        self.assertEqual(alpha[0], [0, 5, 95, 5])
        self.assertEqual(alpha[1], [2, 4, 94, 1])
        self.assertEqual(project["edges"],
                         [{"time": 0, "source": 1, "dest": 2,
                           "ftheta": 0.5, "btheta": 0.1}])
        self.assertEqual(project["parameters"], {"k": "seed", "v": "42"})

    def test_nan_becomes_null(self):
        path = geolibre_export.export_project(self.outdir)
        with open(path, encoding="utf-8") as fobj:
            raw = fobj.read()
        self.assertNotIn("NaN", raw)  # invalid JSON must not be emitted
        project = json.loads(raw)
        beta_step1 = project["series"]["2"][1]
        self.assertIsNone(beta_step1[0])

    def test_explicit_sim_selection(self):
        path = geolibre_export.export_project(
            self.outdir, sim="sim_Mon_Jan_01_000000_2026")
        self.assertTrue(os.path.exists(path))
        with self.assertRaises(ValueError):
            geolibre_export.export_project(self.outdir, sim="nope")

    def test_missing_database(self):
        with self.assertRaises(FileNotFoundError):
            geolibre_export.export_project(os.path.join(self.outdir, "nope"))


if __name__ == "__main__":
    unittest.main()
