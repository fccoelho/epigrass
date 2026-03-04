# Influenza Model

## Overview
This example demonstrates an **Influenza epidemiological model** using Epigrass. The model simulates the spread of influenza across multiple sites connected by a transportation network.

## Model Type
- **Influenza**: A specialized compartmental model for influenza dynamics with multiple compartments including asymptomatic and symptomatic infections.

## Key Parameters
- **beta**: Transmission coefficient, varies with population size
- **r**: Inverse of infectious period (4 days)
- **e**: Inverse of incubation period
- **c, g, d**: Flu-specific parameters for different compartments
- **pc1-pc4, pp1-pp2**: Probability parameters for different infectious states

## Network Topology
- **Sites**: 6 locations defined in `sitios3.csv`
- **Edges**: Transportation connections defined in `edgesout.csv`

## Files
- `flu.epg`: Model definition file
- `sitios3.csv`: Site/population data
- `edgesout.csv`: Network connectivity data

## Running the Model
```bash
cd demos/flu
uv run epirunner flu.epg
```

## Notes
This model implements a detailed influenza transmission dynamics with multiple infectious compartments, making it suitable for studying realistic influenza epidemics in connected populations.
