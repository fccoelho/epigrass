"""Parse, validate and edit Epigrass ``.epg`` model scripts.

Mirrors the semantics of ``Simulate.loadModelScript`` and
``Simulate.evalConfig``/``chkScript`` (Epigrass/manager.py) but in a
non-fatal way: problems are returned as lists of messages instead of
calling ``sys.exit``.
"""
from __future__ import annotations

import configparser
import os
import re
from pathlib import Path

SECTION_RE = re.compile(r"^\s*\[(?P<section>[^\]]+)\]\s*$")
KEYVAL_RE = re.compile(r"^\s*(?P<key>[A-Za-z_]\w*)\s*=(?P<rest>.*)$")

MODEL_TYPES = [
    "SIS", "SIS_s", "SIR", "SIR_s", "SEIS", "SEIS_s", "SEIR", "SEIR_s",
    "SIpRpS", "SIpRpS_s", "SIpR", "SIpR_s", "Influenza", "Custom",
]

#: section -> required option keys (from Simulate.evalConfig)
REQUIRED = {
    "the world": ["sites", "edges", "encoding"],
    "epidemiological model": ["modtype"],
    "model parameters": ["beta", "alpha", "e", "r", "delta", "b", "w", "p"],
    "epidemic events": ["seed", "vaccinate"],
    "transportation model": ["dotransp", "stochastic", "speed"],
    "simulation and output": [
        "steps", "outdir", "sqlout", "report", "siterep", "replicas",
        "randseed", "batch",
    ],
}

#: (section, key) pairs whose values are eval'd by evalConfig
EVAL_KEYS = {
    ("epidemic events", "seed"),
    ("epidemic events", "vaccinate"),
    ("transportation model", "dotransp"),
    ("transportation model", "stochastic"),
    ("transportation model", "speed"),
    ("simulation and output", "steps"),
    ("simulation and output", "sqlout"),
    ("simulation and output", "report"),
    ("simulation and output", "siterep"),
    ("simulation and output", "replicas"),
    ("simulation and output", "randseed"),
    ("simulation and output", "batch"),
}


def parse_epg(path: str | os.PathLike) -> dict[str, str]:
    """Parse an ``.epg`` file into a flat ``{"section.option": value}`` dict.

    Keys are lowercased, exactly like ``Simulate.loadModelScript``.
    """
    cp = configparser.ConfigParser(interpolation=None, strict=False)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        cp.read_file(f)
    config: dict[str, str] = {}
    for sec in cp.sections():
        for opt in cp.options(sec):
            config[f"{sec.lower()}.{opt.lower()}"] = cp.get(sec, opt).strip()
    return config


def _eval_value(value: str):
    return eval(value, {"__builtins__": __builtins__}, {})


def validate_epg(path: str | os.PathLike, parsed: dict[str, str] | None = None) -> list[str]:
    """Return a list of problems with the model script (empty list = valid)."""
    path = Path(path)
    if parsed is None:
        try:
            parsed = parse_epg(path)
        except Exception as exc:
            return [f"Could not parse file: {exc}"]
    errors: list[str] = []
    for sec, keys in REQUIRED.items():
        for key in keys:
            if f"{sec}.{key}" not in parsed:
                errors.append(f"Missing required entry: [{sec}] {key}")
    base = path.parent
    for key in ("sites", "edges"):
        full = f"the world.{key}"
        value = parsed.get(full, "")
        if not value:
            errors.append(f"[the world] {key} file is not set")
        elif not (base / value).is_file():
            errors.append(f"[the world] {key} file not found: {value}")
    modtype = parsed.get("epidemiological model.modtype", "")
    if modtype and modtype not in MODEL_TYPES:
        errors.append(
            f"Invalid model type: {modtype!r} (valid: {', '.join(MODEL_TYPES)})"
        )
    for sec, key in sorted(EVAL_KEYS):
        full = f"{sec}.{key}"
        if full not in parsed:
            continue
        value = parsed[full].split("#")[0]
        try:
            _eval_value(value)
        except Exception as exc:
            errors.append(f"[{sec}] {key}: invalid expression {value!r} ({exc})")
    return errors


def set_values(
    path: str | os.PathLike, updates: dict[tuple[str, str], str]
) -> tuple[int, list[tuple[str, str]]]:
    """Rewrite selected ``key = value`` lines in an ``.epg`` file in place.

    ``updates`` maps ``(section, key)`` (case-insensitive) to the new value
    string.  Comments and formatting on other lines are preserved.  Returns
    ``(n_changed, missing)`` where *missing* lists requested keys that were
    not found in the file.
    """
    path = Path(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    had_final_newline = text.endswith("\n")
    lines = text.splitlines()
    section: str | None = None
    pending = {k: v for k, v in updates.items()}
    changed = 0
    out: list[str] = []
    for line in lines:
        m = SECTION_RE.match(line)
        if m:
            section = m.group("section").strip().lower()
            out.append(line)
            continue
        m = KEYVAL_RE.match(line)
        if m and section is not None:
            key = (section, m.group("key").lower())
            if key in pending:
                rest = m.group("rest")
                comment = ""
                if "#" in rest:
                    idx = rest.index("#")
                    trailing_ws = rest[:idx][len(rest[:idx].rstrip()):]
                    comment = (trailing_ws or " ") + rest[idx:].rstrip()
                out.append(f"{m.group('key')} = {pending[key]}{comment}")
                del pending[key]
                changed += 1
                continue
        out.append(line)
    new_text = "\n".join(out) + ("\n" if had_final_newline else "")
    if changed:
        path.write_text(new_text, encoding="utf-8")
    return changed, sorted(pending)


def find_models(base: str | os.PathLike = ".", max_depth: int = 2) -> list[Path]:
    """Find ``*.epg`` files under *base* (up to *max_depth* subdirectories)."""
    base = Path(base).resolve()
    results: list[Path] = []
    stack = [(base, 0)]
    while stack:
        d, depth = stack.pop()
        try:
            entries = sorted(os.scandir(d), key=lambda e: e.name)
        except OSError:
            continue
        for entry in entries:
            if entry.name.startswith(".") or entry.name.startswith("outdata-"):
                continue
            if entry.is_file() and entry.name.endswith(".epg"):
                results.append(Path(entry.path))
            elif entry.is_dir() and depth < max_depth:
                stack.append((Path(entry.path), depth + 1))
    return sorted(results)


def summarize(path: str | os.PathLike) -> dict:
    """Best-effort summary of a model script for display purposes."""
    path = Path(path)
    info: dict = {"path": path, "name": path.stem, "errors": None}
    try:
        parsed = parse_epg(path)
    except Exception as exc:
        info["error"] = f"parse error: {exc}"
        return info
    info["modtype"] = parsed.get("epidemiological model.modtype", "?")
    steps = parsed.get("simulation and output.steps", "")
    try:
        info["steps"] = int(_eval_value(steps.split("#")[0]))
    except Exception:
        info["steps"] = "?"
    info["sites"] = parsed.get("the world.sites", "")
    info["edges"] = parsed.get("the world.edges", "")
    info["mtime"] = path.stat().st_mtime
    return info


def overview_rows(parsed: dict[str, str]) -> list[tuple[str, str, str]]:
    """(section, key, value) rows in canonical section order."""
    order = [
        "the world", "epidemiological model", "model parameters",
        "initial conditions", "epidemic events", "transportation model",
        "simulation and output",
    ]
    rank = {s: i for i, s in enumerate(order)}
    rows = []
    for full, value in parsed.items():
        sec, key = full.split(".", 1)
        rows.append((sec, key, value))
    rows.sort(key=lambda r: (rank.get(r[0], len(order)), r[0], r[1]))
    return [(s.title(), k, v) for s, k, v in rows]
