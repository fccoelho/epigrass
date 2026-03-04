# Star Network SIR Model

## Overview
This example demonstrates a **SIR (Susceptible-Infected-Recovered) model** on a star network topology. In a star network, all sites connect to a central hub, representing hub-and-spoke transportation systems.

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
- **Edges**: Star connections defined in `star.csv`

## Files
- `star.epg`: Model definition file
- `nodes.csv`: Site/population data
- `star.csv`: Network connectivity data (star topology)

## Running the Model
```bash
cd demos/star
uv run epirunner star.epg
```

## Notes
The star topology is useful for studying epidemic spread in hub-and-spoke systems, such as:
- Airline transportation networks (hub cities)
- Hospital networks (central hospital serving multiple clinics)
- Supply chain networks (central distribution center)

This topology can lead to interesting dynamics where the central hub acts as a super-spreader or bottleneck for epidemic propagation.
