---
name: epigrass-creator
description: Create Epigrass epidemiological models through step-by-step guided specification. Build metapopulation models (SIR, SEIR, SEIS, SIS, SI) with geographic networks. Supports GeoPackage import for real-world spatial data.
version: 1.1.1
metadata:
  openclaw:
    requires:
      env: []
    primaryEnv: null
    bins:
      - python3
    skillKey: epigrass-creator
    emoji: "🦠"
    homepage: https://github.com/fccoelho/epigrass
---

# Epigrass Creator Skill

Create epidemiological metapopulation models using Epigrass through an interactive, step-by-step wizard.

## What is Epigrass?

Epigrass (Epidemiological Geo-referenced Analysis and Simulation System) is a Python library for simulating disease spread across geographic networks.

## Supported Models

| Model | Compartments | Use Case |
|-------|--------------|----------|
| SIR | S, I, R | Diseases with lifelong immunity |
| SEIR | S, E, I, R | Diseases with latent period |
| SEIS | S, E, I | Diseases with temporary immunity |
| SIS | S, I | Diseases with no immunity |
| SI | S, I | Fatal diseases |
| Custom | User-defined | Specialized scenarios |

## Workflow (5 Steps)

1. **Model Selection** - Choose model type
2. **Site Definition** - Define geographic locations (manual, grid, cities, or **GeoPackage import**)
3. **Parameters** - Configure epidemiological parameters
4. **Network** - Define connections between sites
5. **Simulation** - Set simulation settings and generate files

## GeoPackage Support

Import sites directly from GeoPackage (.gpkg) files:
- Supports any geospatial vector data
- Automatic coordinate extraction
- Column mapping for name, population, geocode
- Works with municipal boundaries, health regions, etc.

Requirements: `pip install geopandas` (or fiona as fallback)

## Usage Examples

```
User: Create a dengue model for Brazilian cities
→ Wizard guides through SEIR selection, city list, parameters

User: Build SIR model with 10x10 grid
→ Wizard creates synthetic network

User: Custom model with hospitalization
→ Wizard collects compartments and transitions
```

## Output

- `model.epg` - Epigrass script
- `sites.csv` - Site/node data
- `edges.csv` - Edge/connection data
- `model_spec.json` - Full specification

## Requirements

- Python 3.8+
- epigrass (`pip install epigrass`)
