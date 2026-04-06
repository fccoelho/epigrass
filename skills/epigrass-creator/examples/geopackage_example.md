# GeoPackage Import Example

This example demonstrates importing sites from a GeoPackage file.

## Sample Workflow

### 1. Prepare Your GeoPackage

Create or obtain a GeoPackage with municipal or regional boundaries:

```python
import geopandas as gpd

# Example: Brazilian municipalities
municipios = gpd.read_file('municipios_brasil.gpkg')
print(municipios.columns)
# Output: ['name', 'geocode', 'population', 'geometry', ...]
```

### 2. Use the Wizard

```
🦠 Step 2/5: Define Sites

Options:
1. Enter cities (auto-fetch data)
2. Grid layout (e.g., 5x5)
3. Manual entry
4. Import from GeoPackage (.gpkg)

Choose option (1-4): 4

Enter GeoPackage file path: ./data/municipios.gpkg

📂 Reading GeoPackage: ./data/municipios.gpkg
✓ Found 5570 features

Available columns: ['name', 'geocode', 'population', 'area', 'geometry']

Column mapping:
  Column for site name [name]: name
  Column for population [pop/population]: population
  Column for geocode/id [geocode/id]: geocode

✓ Imported 5570 sites from GeoPackage
```

### 3. Continue with Model Configuration

The wizard will proceed to parameter configuration with all sites loaded.

### 4. Generated Files

```
epigrass_model/
├── model.epg          # Epigrass script
├── sites.csv          # 5570 sites with coordinates
├── edges.csv          # Network connections (auto-generated)
└── model_spec.json    # Full specification
```

#### edges.csv Format

The edges file is automatically generated based on the connection type:

```csv
Source,Dest,flowSD,flowDS,Distance,geoSource,geoDest
Sao_Paulo,Rio_de_Janeiro,500,500,358.5,3550308,3304557
Sao_Paulo,Belo_Horizonte,400,400,489.2,3550308,3106200
Rio_de_Janeiro,Belo_Horizonte,450,450,340.1,3304557,3106200
```

**Columns:**
- **Source/Dest**: Site names
- **flowSD/flowDS**: People flow per timestep (calculated as 1000/distance)
- **Distance**: Haversine distance in km
- **geoSource/geoDest**: Geocodes

**Connection Types:**
- **Full**: All sites connect to all others (N×(N-1) edges)
- **Distance**: Sites within 500km connect
- **Neighbors**: N nearest sites connect
- **Manual**: User-defined edges

## Creating a Sample GeoPackage

```python
import geopandas as gpd
from shapely.geometry import Point

# Create sample data
data = {
    'name': ['Sao_Paulo', 'Rio_de_Janeiro', 'Belo_Horizonte'],
    'geocode': [3550308, 3304557, 3106200],
    'population': [12300000, 6750000, 2530000],
    'geometry': [
        Point(-46.6333, -23.5505),
        Point(-43.1729, -22.9068),
        Point(-43.9345, -19.9167)
    ]
}

gdf = gpd.GeoDataFrame(data, crs='EPSG:4326')
gdf.to_file('sample_cities.gpkg', driver='GPKG')
```

## Tips

- Ensure your GeoPackage has a geometry column
- Population column is optional (defaults to 100,000)
- Geocode column is optional (uses row index)
- Large GeoPackages (>10,000 features) may take time to process

## Troubleshooting

**Error: geopandas not installed**
```bash
pip install geopandas
```

**Error: File not found**
- Check the file path is correct
- Use absolute path if relative doesn't work

**Error: Column not found**
- Check available columns in the GeoPackage
- Use correct column names (case-sensitive)

**Slow import with large files**
- Consider filtering the GeoPackage first
- Import only regions of interest
