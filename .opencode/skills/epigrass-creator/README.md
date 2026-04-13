# Epigrass Creator Skill

Create epidemiological metapopulation models using Epigrass through an interactive, step-by-step wizard.

## Installation

This skill is automatically available in OpenCode when placed in the `.opencode/skills/` directory.

## Usage

Simply ask OpenCode to create an Epigrass model:

```
Create an SIR model for dengue spread
```

Or import from GeoPackage:

```
Create a COVID-19 model using my municipalities.gpkg file
```

## Supported Models

- **SIR**: Measles, chickenpox (lifelong immunity)
- **SEIR**: Dengue, COVID-19 (with incubation period)
- **SEIS**: Influenza (temporary immunity)
- **SIS**: Common cold (no immunity)
- **SI**: HIV/AIDS (fatal diseases)
- **Custom**: User-defined compartments

## Features

- 5 built-in compartmental models
- GeoPackage, Shapefile, and GeoJSON import
- Interactive parameter configuration
- Multiple network connection types
- Automatic edge generation with Haversine distance
- Flow calculation based on distance

## Requirements

```bash
pip install epigrass
pip install geopandas  # For GeoPackage support
```

## Output Files

The skill generates:
- `model.epg` - Epigrass script
- `sites.csv` - Site/node data
- `edges.csv` - Edge/connection data
- `model_spec.json` - Full specification

## Documentation

- Epigrass: https://epigrass.readthedocs.io/
- Repository: https://github.com/fccoelho/epigrass
