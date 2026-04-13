---
name: epigrass-creator
description: Create Epigrass epidemiological models through step-by-step guided specification. Build metapopulation models (SIR, SEIR, SEIS, SIS, SI) with geographic networks. Supports GeoPackage import for real-world spatial data.
license: MIT
compatibility: opencode
metadata:
  homepage: https://github.com/fccoelho/epigrass
  category: modeling
  tags: epidemiology,simulation,network,gis
---

# Epigrass Model Creator

Guide users through creating epidemiological metapopulation models using Epigrass.

## What is Epigrass?

Epigrass (Epidemiological Geo-referenced Analysis and Simulation System) is a Python library for simulating disease spread across geographic networks. It supports metapopulation models where multiple sites (cities, regions) are connected through a network.

## Supported Models

| Model | Compartments | Use Case |
|-------|--------------|----------|
| SIR | S, I, R | Diseases with lifelong immunity (measles, chickenpox) |
| SEIR | S, E, I, R | Diseases with latent period (dengue, COVID-19) |
| SEIS | S, E, I | Diseases with temporary immunity (influenza) |
| SIS | S, I | Diseases with no immunity (common cold) |
| SI | S, I | Fatal diseases (HIV/AIDS) |
| Custom | User-defined | Specialized scenarios |

## Workflow

When a user asks to create an Epigrass model, guide them through these 5 steps:

### Step 1: Model Selection

Present the available models and help the user choose:

```
🦠 Epigrass Model Creation - Step 1/5: Model Selection

| # | Model | Description | Best For |
|---|-------|-------------|----------|
| 1 | SIR | Susceptible-Infectious-Recovered | Diseases with lifelong immunity |
| 2 | SEIR | Susceptible-Exposed-Infectious-Recovered | Diseases with incubation period |
| 3 | SEIS | Susceptible-Exposed-Infectious-Susceptible | Diseases with temporary immunity |
| 4 | SIS | Susceptible-Infectious-Susceptible | Diseases with no immunity |
| 5 | SI | Susceptible-Infectious | Fatal diseases |
| 6 | Custom | User-defined compartments | Specialized scenarios |

Which model type would you like to use?
```

### Step 2: Site Definition

Help the user define geographic sites. Offer these options:

1. **Manual entry** - User provides: Name, Latitude, Longitude, Population, Geocode
2. **Brazilian cities** - User provides city names, fetch data from IBGE
3. **Grid layout** - Create synthetic network (e.g., 5x5 grid)
4. **GeoPackage import** - Import from .gpkg files with column mapping

For GeoPackage import:
- Detect available columns
- Ask user to map columns for: name, population, geocode
- Extract coordinates from geometry centroids
- Handle large datasets (thousands of sites)

Example prompt:
```
Step 2/5: Define Sites

Options:
1. Enter sites manually (Name, Lat, Lon, Pop, Geocode)
2. List Brazilian cities (I'll fetch coordinates)
3. Create a grid layout (e.g., 5x5)
4. Import from GeoPackage (.gpkg) file

How would you like to define your sites?
```

### Step 3: Epidemiological Parameters

Collect model parameters based on the selected model type:

**Common parameters:**
- `beta` (β): Transmission rate (0.1-1.0)
- `gamma` (γ): Recovery rate = 1/infectious_period_days
- `alpha` (α): Non-linear exponent (1.0 = mass action)
- `delta` (δ): Immunity loss rate (0 = permanent)

**SEIR/SEIS additional:**
- `sigma` (σ): Incubation rate = 1/latent_period_days

Example prompt:
```
Step 3/5: Model Parameters

For a 7-day infectious period: γ = 1/7 ≈ 0.14
For a 5-day incubation period: σ = 1/5 = 0.2

Enter parameters (format: parameter=value):
```

### Step 4: Network Connections

Define how sites connect:

1. **Fully connected** - All sites connect to all others
2. **Distance-based** - Sites within threshold connect (e.g., 500km)
3. **Nearest neighbors** - Each site connects to N closest neighbors
4. **Manual** - User specifies connections

Calculate flows using Haversine distance formula:
- Flow inversely proportional to distance
- Generate edges.csv with: Source, Dest, flowSD, flowDS, Distance, geoSource, geoDest

### Step 5: Simulation Settings

Collect simulation configuration:

- `timestep`: Duration of each step in days (default: 1)
- `iterations`: Number of time steps (default: 365 for 1 year)
- `output_dir`: Where to save results

## Output Files

Generate these files in the output directory:

### model.epg
Epigrass script with model configuration:
```python
# Epigrass Model Script
model_type = 'SEIR'
sites_file = 'sites.csv'
edges_file = 'edges.csv'

# Parameters
beta = 0.4
gamma = 0.14
sigma = 0.2

# Simulation
timestep = 1
iterations = 365
```

### sites.csv
Site data with coordinates and population:
```csv
X,Y,City,Pop,Geocode
-23.5505,-46.6333,Sao_Paulo,12300000,3550308
-22.9068,-43.1729,Rio_de_Janeiro,6750000,3304557
```

### edges.csv
Network connections with distance-based flow:
```csv
Source,Dest,flowSD,flowDS,Distance,geoSource,geoDest
Sao_Paulo,Rio_de_Janeiro,500,500,358.5,3550308,3304557
```

### model_spec.json
Complete specification in JSON format for reproducibility.

## Helper Functions

### Haversine Distance

Use this formula to calculate distances between sites:

```python
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c
```

### Flow Calculation

Calculate flow inversely proportional to distance:
```python
flow = max(10, int(1000 / (distance_km + 1)))
```

## Requirements

Before creating models, ensure the user has:
- Python 3.8+
- epigrass installed: `pip install epigrass`
- For GeoPackage support: `pip install geopandas` or `pip install fiona`

## Example Interactions

**Example 1: Simple SIR model**
```
User: Create a simple SIR model for 3 cities

Agent: I'll help you create an SIR model. Let's start:

Step 1: Selected SIR model (diseases with lifelong immunity)

Step 2: Please provide your 3 cities:
Format: Name, Latitude, Longitude, Population, Geocode
```

**Example 2: Dengue SEIR model**
```
User: Build a dengue model for Brazilian state capitals

Agent: Dengue has an incubation period, so SEIR is the best choice.

Step 1: Selected SEIR model

Step 2: Which capitals would you like to include?
Options: São Paulo, Rio de Janeiro, Belo Horizonte, Brasília, Salvador, etc.
```

**Example 3: GeoPackage import**
```
User: Create a model using my municipalities.gpkg file

Agent: I'll import sites from your GeoPackage.

Step 2: Reading municipalities.gpkg...
Found 5570 features with columns: [name, population, geocode, geometry]

Column mapping:
- Site name column [name]: 
- Population column [population]: 
- Geocode column [geocode]: 

Imported 5570 sites successfully!
```

## Best Practices

1. **Validate inputs** - Check coordinates are valid, populations are positive
2. **Provide defaults** - Suggest reasonable parameter values based on disease type
3. **Explain parameters** - Help users understand what each parameter means
4. **Test small first** - For large networks, suggest testing with fewer sites first
5. **Document assumptions** - Record any assumptions made during model creation

## Final Summary

After generating files, provide a summary:

```
✅ Model Created Successfully!

Model Type: SEIR
Sites: 10
Edges: 45
Parameters: beta=0.4, gamma=0.14, sigma=0.2

Files generated in ./epigrass_model/:
- model.epg (Epigrass script)
- sites.csv (Site data)
- edges.csv (Network connections)
- model_spec.json (Full specification)

To run the simulation:
cd epigrass_model && epirunner model.epg
```

## When to Use This Skill

Use this skill when the user:
- Wants to create an epidemiological model
- Mentions Epigrass or metapopulation models
- Needs to simulate disease spread across geographic regions
- Has spatial data (GeoPackage, Shapefile) to import
- Wants to build SIR, SEIR, or similar compartmental models

Ask clarifying questions if the target disease, region, or model requirements are unclear.
