# Mesh Network SIR Model

## Overview
This example demonstrates a **SIR (Susceptible-Infected-Recovered) model** on a mesh network topology. The mesh network represents a fully-connected or highly-connected set of sites.

## Model Type
- **SIR**: Classic Susceptible-Infected-Recovered compartmental model

## Key Parameters
- **beta**: 0.4 (transmission coefficient)
- **alpha**: 1 (clumping parameter)
- **e**: 1 (inverse of incubation period)
- **r**: 0.1 (inverse of infectious period - 10 days)
- **delta**: 1 (probability of acquiring full immunity)

## Network Topology
- **Sites**: Nodes defined in `nodes.csv`
- **Edges**: Mesh connections defined in `mesh.csv`

## Files
- `mesh.epg`: Model definition file
- `nodes.csv`: Site/population data
- `mesh.csv`: Network connectivity data (mesh topology)

## Running the Model
```bash
cd demos/mesh
uv run epirunner mesh.epg
```

## Notes
The mesh topology allows for studying epidemic spread in highly connected networks, which can represent urban areas with extensive interconnections or small communities with frequent contact between all members.
