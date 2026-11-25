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

    :param outdir: directory holding the run's ``Epigrass.sqlite``
    :param sim: simulation table name; defaults to the newest one
    :returns: path of the written ``.geolibre.json`` file (as str)
    """
    outdir = os.path.abspath(outdir)
    with _connect(outdir) as con:
        sim = _resolve_sim(con, sim)
        parameters = _read_meta(con, sim)

        rows = con.execute(
            f'SELECT * FROM "{sim}" ORDER BY geocode, time').fetchall()
        if not rows:
            raise ValueError(f"Simulation table {sim!r} is empty")

        all_cols = list(rows[0].keys())
        variables = [c for c in all_cols if c not in KEY_COLUMNS]

        # Sites in first-seen order; series aligned to the global time axis.
        sites = {}
        series = {}
        times = set()
        for row in rows:
            gc = row["geocode"]
            if gc not in sites:
                sites[gc] = {
                    "geocode": gc,
                    "name": row["name"],
                    "lat": _clean(row["lat"]),
                    "lon": _clean(row["longit"]),
                }
                series[gc] = []
            times.add(row["time"])
            series[gc].append([_clean(row[v]) for v in variables])

        edges = []
        edge_table = f"{sim}e"
        has_edges = con.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            (edge_table,)).fetchone()
        if has_edges:
            for row in con.execute(
                    f'SELECT * FROM "{edge_table}" ORDER BY time, source_code'):
                if row["source_code"] is None:
                    continue
                edges.append({
                    "time": row["time"],
                    "source": row["source_code"],
                    "dest": row["dest_code"],
                    "ftheta": _clean(row["ftheta"]),
                    "btheta": _clean(row["btheta"]),
                })

    project = {
        "format": "epigrass-geolibre-project",
        "version": 1,
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "simulation": sim,
        "model": sim.split("_")[0],
        "parameters": {k: _clean(v) for k, v in parameters.items()},
        "sites": list(sites.values()),
        "times": sorted(times),
        "variables": variables,
        "series": {str(gc): s for gc, s in series.items()},
    }
    if edges:
        project["edges"] = edges

    out_path = os.path.join(outdir, f"{sim}.geolibre.json")
    with open(out_path, "w", encoding="utf-8") as fobj:
        json.dump(project, fobj, ensure_ascii=False, allow_nan=False)
    return out_path
