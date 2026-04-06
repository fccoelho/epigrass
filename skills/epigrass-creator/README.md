# 🦠 Epigrass Creator Skill

Create epidemiological metapopulation models using Epigrass through an interactive wizard.

## Quick Start

```bash
npx clawhub install epigrass-creator
```

Then ask your OpenClaw agent:
```
"Create an SIR model for dengue spread"
```

Or import from GeoPackage:
```
"Create a COVID-19 model using my municipalities.gpkg file"
```

## Supported Models

- **SIR**: Measles, chickenpox
- **SEIR**: Dengue, COVID-19 (with incubation)
- **SEIS**: Influenza (temporary immunity)
- **SIS**: Common cold (no immunity)
- **SI**: HIV/AIDS (fatal)
- **Custom**: User-defined compartments

## Example Session

```
User: Create a dengue model for São Paulo and Rio

Agent: 🦠 Epigrass Wizard - Step 1/5
       Select model type:
       1. SIR
       2. SEIR ← Best for dengue
       3. SEIS
       4. SIS
       5. SI
       6. Custom

User: 2

Agent: ✓ SEIR selected
       
       Step 2/5: Define sites
       Enter cities (comma-separated):

User: São Paulo, Rio de Janeiro

Agent: ✓ Found 2 cities
       
       Step 3/5: Parameters
       beta (transmission rate, 0.1-1.0): 0.4
       gamma (recovery, 1/days): 0.14
       sigma (incubation, 1/days): 0.2

Agent: ✓ Parameters set

       Step 4/5: Network connections
       1. Fully connected
       2. Distance-based
       3. Manual

User: 2

Agent: Step 5/5: Simulation
       Days to simulate: 365
       Output directory: ./dengue_model

Agent: ✅ Model created!
       Files: model.epg, sites.csv, edges.csv
       Run: epirunner model.epg
```

## GeoPackage Import

Import sites directly from GeoPackage files:

```
User: Create a model using my data/municipalities.gpkg

Agent: 📂 Reading GeoPackage: data/municipalities.gpkg
       ✓ Found 5570 features
       
       Available columns: [name, population, geocode, geometry, area]
       
       Column mapping:
         Column for site name [name]: 
         Column for population [pop/population]: population
         Column for geocode/id [geocode/id]: geocode
       
       ✓ Imported 5570 sites
```

### Requirements

```bash
pip install geopandas  # Recommended
# or
pip install fiona      # Lightweight alternative
```

### Supported Formats

The wizard can read any OGR vector format supported by geopandas/fiona:
- GeoPackage (.gpkg)
- Shapefile (.shp)
- GeoJSON (.geojson)
- PostGIS (via connection string)

## Output Files

The wizard generates 4 files:

### model.epg
Epigrass script with model configuration.

### sites.csv
Site data with coordinates and population:
```csv
X,Y,City,Pop,Geocode
-23.5505,-46.6333,Sao_Paulo,12300000,3550308
-22.9068,-43.1729,Rio_de_Janeiro,6750000,3304557
```

### edges.csv
**Network connections (auto-generated)**:
```csv
Source,Dest,flowSD,flowDS,Distance,geoSource,geoDest
Sao_Paulo,Rio_de_Janeiro,500,500,358.5,3550308,3304557
```

Edges are automatically created based on:
- **Full**: All sites connect to all others
- **Distance**: Sites within 500km connect
- **Neighbors**: N nearest neighbors
- **Manual**: User-specified connections

Flow values are calculated inversely proportional to distance.

### model_spec.json
Complete model specification in JSON format.

## Documentation

- Epigrass: https://epigrass.readthedocs.io/
- OpenClaw: https://clawhub.ai
