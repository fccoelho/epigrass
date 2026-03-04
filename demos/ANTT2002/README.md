# ANTT 2002 Brazilian Transportation Network Data

## Overview
This directory contains **transportation network data** from the Brazilian National Land Transport Agency (ANTT) from 2002. This dataset provides real-world mobility data between Brazilian municipalities and can be used to build epidemiological models based on actual transportation flows.

## Data Description

This is a **data resource** rather than a complete epidemiological model. It provides the network topology and flow data needed to construct realistic epidemic simulations in Brazil.

### Files

- **`antt2002.csv`**: Main transportation flow data
  - Contains passenger flows between Brazilian municipalities
  - Includes: municipality names, states, passengers (round-trip), and passenger-kilometers
  - Format: `n, municipio1, uf1, municipio2, uf2, pass ida, pass volta, pass total, passxkm`

- **`antt2002TODOS.csv`**: Extended/complete transportation data
  - Comprehensive version of the transportation dataset
  - Includes additional routes and municipalities

- **`centroides.csv`**: Geographic coordinates
  - Contains centroid coordinates for each municipality
  - Format: Municipality code, latitude/longitude coordinates
  - Useful for geographic visualization and distance calculations

- **`codigos_sitios.csv`**: Site code mapping
  - Maps sequential IDs to Brazilian municipality codes (geocodes)
  - Format: `x, codigo`

## Data Structure

### Transportation Flows (antt2002.csv)
```
n,municipio1,uf1,municipio2,uf2,pass ida,pass volta,pass total,passxkm
1,ANAPOLIS,GO,CAMPINAS,SP,2737,2882,5619,5008504
2,ANAPOLIS,GO,CUIABA,MT,1514,1633,3147,3170961
```

Where:
- `municipio1, uf1`: Origin municipality and state
- `municipio2, uf2`: Destination municipality and state
- `pass ida`: Passengers traveling from origin to destination
- `pass volta`: Passengers returning from destination to origin
- `pass total`: Total passengers (both directions)
- `passxkm`: Passenger-kilometers (flow × distance)

## Using This Data

To create an epidemiological model using this data:

1. **Create a sites file**: Extract unique municipalities with population data
2. **Create an edges file**: Convert transportation flows to edge weights
3. **Create a model file (.epg)**: Define your epidemiological model
4. **Optional**: Use centroides.csv for geographic visualization

### Example Conversion

```python
import pandas as pd

# Load transportation data
antt_data = pd.read_csv('antt2002.csv')

# Create sites file
sites = set()
for _, row in antt_data.iterrows():
    sites.add((row['municipio1'], row['uf1']))
    sites.add((row['municipio2'], row['uf2']))

# Create edges file with flow weights
edges = antt_data[['municipio1', 'municipio2', 'pass total']].copy()
edges.columns = ['source', 'target', 'flow']
edges.to_csv('edges.csv', index=False)
```

## Potential Applications

This dataset can be used to study:
- Epidemic spread through Brazil's transportation network
- Hub-and-spoke patterns in disease transmission
- Impact of inter-municipal travel on disease dynamics
- Regional outbreak patterns in Brazil
- Network-based intervention strategies

## Notes

- Data is from **2002**, representing the Brazilian inter-municipal transportation network at that time
- Passenger flows represent **actual recorded trips**, not estimated
- The network includes **both directions** of travel (ida/volta)
- Useful for **retrospective analysis** or as a template for modern datasets

## Related Examples

See the `rio/` example for a complete epidemiological model using Brazilian geographic and mobility data for Rio de Janeiro.
