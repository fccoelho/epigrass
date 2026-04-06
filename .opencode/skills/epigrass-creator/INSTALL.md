# OpenCode Skill: Epigrass Creator

This repository contains the OpenCode skill for creating Epigrass epidemiological models.

## Installation

### Option 1: Clone to global skills directory

```bash
mkdir -p ~/.config/opencode/skills
git clone https://github.com/fccoelho/opencode-skill-epigrass.git ~/.config/opencode/skills/epigrass-creator
```

### Option 2: Clone to project-level skills

```bash
mkdir -p .opencode/skills
git clone https://github.com/fccoelho/opencode-skill-epigrass.git .opencode/skills/epigrass-creator
```

### Option 3: Manual installation

Copy the `epigrass-creator` folder to:
- `~/.config/opencode/skills/` (global)
- `.opencode/skills/` (project-level)

## Usage

Once installed, ask OpenCode to create an Epigrass model:

```
Create an SIR model for dengue spread
```

Or import from GeoPackage:

```
Create a COVID-19 model using my municipalities.gpkg file
```

## Features

- 5 built-in compartmental models (SIR, SEIR, SEIS, SIS, SI)
- Custom model support
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

## Documentation

- Epigrass: https://epigrass.readthedocs.io/
- Repository: https://github.com/fccoelho/epigrass
- OpenCode: https://opencode.ai

## License

MIT
