# Example: Creating a Dengue SEIR Model

This example demonstrates how to use the epigrass-creator skill to build a dengue model for Brazilian state capitals.

## User Request

```
Create a dengue SEIR model for São Paulo, Rio de Janeiro, and Belo Horizonte
```

## Step-by-Step Interaction

### Step 1: Model Selection

Agent: Since dengue has an incubation period, I recommend the SEIR model.

```
Selected: SEIR (Susceptible-Exposed-Infectious-Recovered)
```

### Step 2: Site Definition

Agent: I'll help you define the three cities. Let me fetch their data:

```
Site 1: São Paulo
  - Coordinates: -23.5505, -46.6333
  - Population: 12,330,000
  - Geocode: 3550308

Site 2: Rio de Janeiro
  - Coordinates: -22.9068, -43.1729
  - Population: 6,750,000
  - Geocode: 3304557

Site 3: Belo Horizonte
  - Coordinates: -19.9167, -43.9345
  - Population: 2,720,000
  - Geocode: 3106200

Total sites: 3
```

### Step 3: Parameters

Agent: For dengue, I suggest these parameter values:

```
beta (transmission rate): 0.4
gamma (recovery rate, 1/7 days): 0.14
sigma (incubation rate, 1/5 days): 0.2
alpha (exponent): 1.0

Parameters configured successfully
```

### Step 4: Network Connections

Agent: How would you like to connect these cities?

User: Fully connected

```
Connection type: Fully connected
Generating 6 edges (3 bidirectional connections)
```

### Step 5: Simulation Settings

Agent: Configure the simulation:

```
Timestep: 1 day
Iterations: 365 (1 year)
Output directory: ./dengue_model
```

## Generated Files

### model.epg

```python
# Epigrass Model Script
# Generated: 2026-04-06
# Model Type: SEIR

model_type = 'SEIR'
sites_file = 'sites.csv'
edges_file = 'edges.csv'

# Parameters
beta = 0.4
gamma = 0.14
sigma = 0.2
alpha = 1.0

# Simulation
timestep = 1
iterations = 365
```

### sites.csv

```csv
X,Y,City,Pop,Geocode
-23.5505,-46.6333,Sao_Paulo,12330000,3550308
-22.9068,-43.1729,Rio_de_Janeiro,6750000,3304557
-19.9167,-43.9345,Belo_Horizonte,2720000,3106200
```

### edges.csv

```csv
Source,Dest,flowSD,flowDS,Distance,geoSource,geoDest
Sao_Paulo,Rio_de_Janeiro,500,500,358.5,3550308,3304557
Sao_Paulo,Belo_Horizonte,450,450,586.3,3550308,3106200
Rio_de_Janeiro,Belo_Horizonte,400,400,439.2,3304557,3106200
```

### model_spec.json

```json
{
  "model_type": "SEIR",
  "sites": [
    {
      "name": "Sao_Paulo",
      "lat": -23.5505,
      "lon": -46.6333,
      "population": 12330000,
      "geocode": "3550308"
    },
    {
      "name": "Rio_de_Janeiro",
      "lat": -22.9068,
      "lon": -43.1729,
      "population": 6750000,
      "geocode": "3304557"
    },
    {
      "name": "Belo_Horizonte",
      "lat": -19.9167,
      "lon": -43.9345,
      "population": 2720000,
      "geocode": "3106200"
    }
  ],
  "parameters": {
    "beta": 0.4,
    "gamma": 0.14,
    "sigma": 0.2,
    "alpha": 1.0
  },
  "simulation": {
    "timestep": 1,
    "iterations": 365
  },
  "output_dir": "./dengue_model"
}
```

## Running the Model

```bash
cd dengue_model
epirunner model.epg
```

## Summary

```
✅ Model Created Successfully!

Model Type: SEIR
Sites: 3
Edges: 6 (3 bidirectional)
Parameters: beta=0.4, gamma=0.14, sigma=0.2, alpha=1.0

Files generated in ./dengue_model/:
- model.epg
- sites.csv
- edges.csv
- model_spec.json

To run: cd dengue_model && epirunner model.epg
```
