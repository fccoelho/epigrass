# Florida Counties SEIR Model

## Overview
This example demonstrates a **SEIR (Susceptible-Exposed-Infected-Recovered) model** for epidemiological simulation across Florida counties. The model includes geographic visualization using GIS shapefiles and implements control measures with a delay.

## Model Type
- **SEIR**: Susceptible-Exposed-Infected-Recovered compartmental model

## Key Parameters
- **beta**: 0.65 (transmission coefficient)
- **alpha**: 1 (clumping parameter)
- **e**: 0.14 (inverse of incubation period - 7 days)
- **r**: 0.1 (inverse of infectious period - 10 days)
- **delta**: 0 (probability of acquiring full immunity)
- **tau**: 30 (delay in the start of control measures)
- **k**: 0.0023 (reduction in transmission due to controls)

## Network Topology
- **Sites**: 67 Florida counties defined in `sites.csv`
- **Edges**: 3,550 mobility connections between counties defined in `edges.csv`
- **Shapefile**: Geographic visualization using `Florida_2000.shp`

## Files
- `florida.epg`: Model definition file
- `sites.csv`: Site/population data for Florida counties (67 counties)
- `edges.csv`: Network connectivity data (mobility between counties)
- `Florida_2000.shp/dbf/shx`: Shapefile for geographic visualization
- `spread.gml`: Graph export in GML format (from previous simulation)
- `spread.graphml`: Graph export in GraphML format (from previous simulation)
- `epimodels.log`: Log file from previous simulation runs

## Running the Model
```bash
cd demos/Florida
uv run epirunner florida.epg
```

## Notes
This model represents a realistic scenario with:
- **67 Florida counties** as network nodes
- **Extensive mobility data** with over 3,500 connections between counties
- **Control measures** that begin after a 30-day delay
- **Transmission reduction** factor (k) applied after control measures start

The model is suitable for studying:
- County-level epidemic spread in Florida
- Impact of delayed intervention strategies
- Geographic visualization of disease dynamics
- Network-based transmission in a real administrative division

The shapefile provides visual context for the epidemic spread across Florida's counties, making it ideal for geographic analysis and presentation.

## Data Sources
The mobility data between counties likely represents commuting patterns or transportation flows, making this a realistic model for studying epidemic spread through daily human movement patterns.
