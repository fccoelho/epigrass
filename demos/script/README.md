# Script Custom Model

## Overview
This example demonstrates a **custom epidemiological model** that serves as a template or example for implementing custom disease dynamics in Epigrass.

## Model Type
- **Custom**: A custom model implementation

## Key Parameters
- **beta**: 0.6 (transmission coefficient - calibrated for R0 ≈ 3, based on Lipsitch 2003)
- **alpha**: 1 (clumping parameter)
- **e**: 1 (inverse of incubation period - 1 day)
- **r**: 0.1 (inverse of infectious period - 10 days)
- **delta**: 1 (probability of acquiring full immunity)

## Network Topology
- **Sites**: 6 locations defined in `sitios3.csv`
- **Edges**: Transportation connections defined in `edgesout.csv`

## Files
- `script.epg`: Model definition file
- `sitios3.csv`: Site/population data
- `edgesout.csv`: Network connectivity data

## Running the Model
```bash
cd demos/script
uv run epirunner script.epg
```

## Notes
This model can be used as a starting point for implementing custom epidemiological models. The parameters are based on published literature (Lipsitch 2003) for respiratory infections. Users can modify the model definition to implement specific disease dynamics as needed.
