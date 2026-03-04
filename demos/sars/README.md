# SARS Custom Model

## Overview
This example demonstrates a **custom epidemiological model** designed for SARS (Severe Acute Respiratory Syndrome) simulation across a network of connected sites.

## Model Type
- **Custom**: A custom model implementation for SARS dynamics

## Key Parameters
- **beta**: 1.4 (transmission coefficient - calibrated for R0 ≈ 3)
- **alpha**: 1 (clumping parameter)
- **e**: 0.2 (inverse of incubation period - 5 days)
- **r**: 0.2 (inverse of infectious period - 5 days)
- **delta**: 0 (probability of acquiring full immunity)

## Network Topology
- **Sites**: 6 locations defined in `sitios3.csv`
- **Edges**: Transportation connections defined in `edgesout.csv`

## Files
- `sars.epg`: Model definition file
- `sitios3.csv`: Site/population data
- `edgesout.csv`: Network connectivity data

## Running the Model
```bash
cd demos/sars
uv run epirunner sars.epg
```

## Notes
This model uses a custom implementation to capture the specific dynamics of SARS transmission. The transmission coefficient is calibrated to achieve a basic reproduction number (R0) around 3, which is consistent with SARS outbreak characteristics.
