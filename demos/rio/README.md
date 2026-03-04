# Rio de Janeiro SEIR Model

## Overview
This example demonstrates a **SEIR continuous model (SEIR_cont)** for epidemiological simulation in Rio de Janeiro, Brazil. This model includes geographic visualization using GIS shapefiles.

## Model Type
- **SEIR_cont**: Susceptible-Exposed-Infected-Recovered continuous model, which uses continuous-time dynamics rather than discrete time steps.

## Key Parameters
- **beta**: 1 (transmission coefficient)
- **alpha**: 1 (clumping parameter)
- **e**: 0.2 (inverse of incubation period - 5 days)
- **r**: 0.2 (inverse of infectious period - 5 days)
- **delta**: 0 (probability of acquiring full immunity)

## Network Topology
- **Sites**: Traffic zones of Rio de Janeiro defined in `sites.csv`
- **Edges**: Mobility connections between zones defined in `edges.csv`
- **Shapefile**: Geographic visualization using `riozonas_LatLong.shp`

## Files
- `rio.epg`: Model definition file
- `sites.csv`: Site/population data for Rio de Janeiro traffic zones
- `edges.csv`: Network connectivity data (mobility between zones)
- `edgesRIO.csv`: Alternative edge data with detailed flow information
- `sitios2.csv`: Alternative site data with Brazilian cities
- `riozonas_LatLong.shp/dbf/shx`: Shapefile for geographic visualization
- `zonasRJcompleto.csv`: Additional data for Rio de Janeiro zones

## Running the Model
```bash
cd demos/rio
uv run epirunner rio.epg
```

## Notes
This is a realistic model using actual geographic and mobility data from Rio de Janeiro. The shapefile provides visual context for the epidemic spread across the city's traffic zones. The continuous-time model allows for more accurate simulation of disease dynamics.
