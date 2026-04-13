# Example: Importing Sites from GeoPackage

This example demonstrates how to import sites from a GeoPackage file to create a large-scale epidemiological model.

## User Request

```
Create a COVID-19 model using my municipalities.gpkg file with Brazilian municipalities
```

## Step-by-Step Interaction

### Step 1: Model Selection

Agent: For COVID-19, I recommend the SEIR model due to the incubation period.

```
Selected: SEIR (Susceptible-Exposed-Infectious-Recovered)
```

### Step 2: GeoPackage Import

Agent: I'll import sites from your GeoPackage file.

```
📂 Reading GeoPackage: municipalities.gpkg
✓ Found 5570 features

Available columns:
- name (municipality name)
- geocode (IBGE code)
- population (2020 estimate)
- state (state abbreviation)
- area_km2 (area in km²)
- geometry (polygon boundaries)

Column mapping:
  Column for site name [name]: name
  Column for population [pop/population]: population
  Column for geocode/id [geocode/id]: geocode

✓ Extracting coordinates from geometry centroids...
✓ Imported 5570 sites from GeoPackage
```

### Step 3: Parameters

Agent: For COVID-19, I suggest these parameters:

```
beta (transmission rate): 0.5
gamma (recovery rate, ~14 days infectious): 0.07
sigma (incubation rate, ~5 days): 0.2
alpha (exponent): 1.0

Note: For COVID-19, the basic reproduction number R0 = beta/gamma
With these values: R0 ≈ 7.14 (adjust based on your needs)
```

### Step 4: Network Connections

Agent: With 5570 sites, I recommend distance-based connections:

```
Connection type: Distance-based
Threshold: 200 km (sites within 200km will be connected)

This will create approximately 150,000-200,000 edges
Calculation time: ~2-3 minutes

Proceed? (yes/no): yes

✓ Generated 187,432 edges
```

### Step 5: Simulation Settings

```
Timestep: 1 day
Iterations: 180 (6 months)
Output directory: ./covid19_model
```

## Generated Files

### sites.csv (excerpt)

```csv
X,Y,City,Pop,Geocode
-23.5505,-46.6333,Sao_Paulo,12330000,3550308
-22.9068,-43.1729,Rio_de_Janeiro,6750000,3304557
-19.9167,-43.9345,Belo_Horizonte,2720000,3106200
-12.9714,-38.5014,Salvador,2887000,2927408
... (5570 rows total)
```

### edges.csv (excerpt)

```csv
Source,Dest,flowSD,flowDS,Distance,geoSource,geoDest
Sao_Paulo,Campinas,850,850,79.4,3550308,3509502
Sao_Paulo,Santos,720,720,70.2,3550308,3548500
Sao_Paulo,Sao_Jose_dos_Campos,680,680,88.3,3550308,3549904
... (187,432 rows total)
```

## Performance Considerations

For large networks (5000+ sites):

1. **Distance-based connections** recommended over fully connected
2. **Threshold tuning**: Adjust distance threshold to control edge count
3. **Computation time**: Expect 2-5 minutes for edge generation
4. **Memory**: Requires ~500MB-1GB RAM for 5000+ sites
5. **Parallel processing**: Consider using multiprocessing for very large networks

## Alternative: Filter by State

If you want a smaller model for a specific state:

```
User: Create model only for São Paulo state municipalities

Agent: I can filter the GeoPackage to include only São Paulo state.

Filtering by state = 'SP'...
✓ Found 645 municipalities in São Paulo state

This will create a more manageable model with ~20,000-30,000 edges.
```

## Tips for Large Datasets

1. **Test with subset first**: Import 100-500 sites to verify parameters
2. **Use distance threshold**: Prevents excessive edge creation
3. **Consider aggregation**: Aggregate municipalities by health region
4. **Batch processing**: Process edges in batches for very large networks
5. **Memory monitoring**: Watch memory usage during edge generation

## Requirements

```bash
# Required for GeoPackage support
pip install geopandas

# Alternative (lighter weight)
pip install fiona
```
