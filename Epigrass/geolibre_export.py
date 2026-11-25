"""
Export Epigrass simulation results as a GeoLibre project file.

A GeoLibre project is a self-describing ``.geolibre.json`` file bundling
everything needed to visualize a simulation run on a map: metadata, site
coordinates, per-site time series and the migration (edge) events.

Schema (version 1)::

    {
      "format": "epigrass-geolibre-project",
      "version": 1,
      "generated": "<ISO-8601 UTC timestamp>",
      "simulation": "<sqlite table name>",
      "model": "<model name>",
      "parameters": { ...contents of the <sim>_meta table ... },
      "sites": [
        {"geocode": 240800305, "name": "Abaeté", "lat": -19.35, "lon": -45.1},
        ...
      ],
      "times": [0, 1, 2, ...],
      "variables": ["Exposed", "Infectious", "Susceptible", "incidence"],
      "series": {
        "<geocode>": [[E0, I0, S0, inc0], [E1, I1, S1, inc1], ...],
        ...
      },
      "edges": [                       // optional, present when the run logged them
        {"time": 3, "source": 3100104, "dest": 3304557, "ftheta": 0.4, "btheta": 0.1},
        ...
      ]
    }

Usage::

    from Epigrass import geolibre_export
    path = geolibre_export.export_project("outdata-sars")            # newest run
    path = geolibre_export.export_project("outdata-sars", sim="sars_Wed_Nov_25_170752_2026")
"""

import json
import os
import sqlite3
from datetime import datetime, timezone
from itertools import groupby

KEY_COLUMNS = {"geocode", "time", "name", "lat", "longit"}
EDGE_COLUMNS = {"source_code", "dest_code"}


def _connect(outdir: str) -> sqlite3.Connection:
    db = os.path.join(outdir, "Epigrass.sqlite")
    if not os.path.exists(db):
        raise FileNotFoundError(f"No Epigrass.sqlite found in {outdir!r}")
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    return con


def _data_tables(con: sqlite3.Connection) -> list:
    """Simulation data tables, ordered by name (same order as the dashboards)."""
    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    data = []
    for t in tables:
        if t.endswith("_meta"):
            continue
        cols = {r[1] for r in con.execute(f'PRAGMA table_info("{t}")')}
        if EDGE_COLUMNS.issubset(cols):  # migration-events table
            continue
        if {"geocode", "time"}.issubset(cols):
            data.append(t)
    return data


def _resolve_sim(con: sqlite3.Connection, sim: str = None) -> str:
    tables = _data_tables(con)
    if sim:
        if sim in tables:
            return sim
        raise ValueError(
            f"Simulation {sim!r} not found. Available: {tables or 'none'}")
    if not tables:
        raise ValueError("No simulation tables found in Epigrass.sqlite")
    return tables[-1]  # newest by name, same convention as the dashboards


def _read_meta(con: sqlite3.Connection, sim: str) -> dict:
    meta_table = f"{sim}_meta"
    exists = con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (meta_table,)).fetchone()
    if not exists:
        return {}
    row = con.execute(f'SELECT * FROM "{meta_table}"').fetchone()
    return {k: row[k] for k in row.keys()} if row is not None else {}


def _clean(value):
    """Make a value JSON-safe (NaN/None become null)."""
    if value is None:
        return None
    try:
        if value != value:  # NaN
            return None
    except TypeError:
        return str(value)
    return value


def export_project(outdir: str, sim: str = None) -> str:
    """Write a ``<sim>.geolibre.json`` project into `outdir`.

    Streams the per-site series straight to disk (one site in memory at a
    time), so exporting millions of rows costs seconds and constant memory
    instead of freezing the dashboard server.

    :param outdir: directory holding the run's ``Epigrass.sqlite``
    :param sim: simulation table name; defaults to the newest one
    :returns: path of the written ``.geolibre.json`` file (as str)
    """
    outdir = os.path.abspath(outdir)
    with _connect(outdir) as con:
        sim = _resolve_sim(con, sim)
        parameters = _read_meta(con, sim)

        cols = [r[1] for r in con.execute(f'PRAGMA table_info("{sim}")')]
        variables = [c for c in cols if c not in KEY_COLUMNS]
        var_sql = ", ".join(f'"{v}"' for v in variables)

        times = [r[0] for r in con.execute(
            f'SELECT DISTINCT time FROM "{sim}" ORDER BY time')]
        sites = [{"geocode": r[0], "name": r[1],
                  "lat": _clean(r[2]), "lon": _clean(r[3])}
                 for r in con.execute(
                     f'SELECT geocode, name, lat, longit FROM "{sim}" '
                     f'GROUP BY geocode ORDER BY geocode')]

        out_path = os.path.join(outdir, f"{sim}.geolibre.json")
        with open(out_path, "w", encoding="utf-8") as fobj:
            write = fobj.write
            write('{"format": "epigrass-geolibre-project", "version": 1, ')
            write(f'"generated": {json.dumps(datetime.now(timezone.utc).isoformat(timespec="seconds"))}, ')
            write(f'"simulation": {json.dumps(sim)}, ')
            write(f'"model": {json.dumps(sim.split("_")[0])}, ')
            write(f'"parameters": {json.dumps(parameters, ensure_ascii=False)}, ')
            write(f'"sites": {json.dumps(sites, ensure_ascii=False)}, ')
            write(f'"times": {json.dumps(times)}, ')
            write(f'"variables": {json.dumps(variables)}, ')
            write('"series": {')

            cur = con.execute(
                f'SELECT geocode, {var_sql} FROM "{sim}" ORDER BY geocode, time')
            first_site = True
            for geocode, grp in groupby(map(tuple, cur), key=lambda t: t[0]):
                series = [[_clean(v) for v in t[1:]] for t in grp]
                if not first_site:
                    write(",")
                first_site = False
                write(f'{json.dumps(str(geocode))}: '
                      f'{json.dumps(series, allow_nan=False, ensure_ascii=False)}')
            write("}")

            # Migration events, if the run logged them
            edge_table = f"{sim}e"
            has_edges = con.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (edge_table,)).fetchone()
            if has_edges:
                write(', "edges": [')
                first_edge = True
                for r in con.execute(
                        f'SELECT time, source_code, dest_code, ftheta, btheta '
                        f'FROM "{edge_table}" ORDER BY time, source_code'):
                    if r[1] is None:
                        continue
                    if not first_edge:
                        write(",")
                    first_edge = False
                    write(json.dumps({"time": r[0], "source": r[1],
                                      "dest": r[2], "ftheta": _clean(r[3]),
                                      "btheta": _clean(r[4])}))
                write("]")

            write("}")

    return out_path
