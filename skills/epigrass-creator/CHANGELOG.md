# Changelog

All notable changes to the Epigrass Creator Skill will be documented in this file.

## [1.1.1] - 2026-04-06

### Fixed
- **Documentation accuracy** - Removed PostGIS mention (not implemented)
- **Clarified city entry option** - Changed "auto-fetch" to "manual coordinate entry" with warning
- **Removed misleading comments** - Removed "would fetch from IBGE" comment
- **Version consistency** - All files now reference version 1.1.1

## [1.1.0] - 2026-04-06

### Added
- **GeoPackage import support** - Import sites directly from .gpkg files
- **Shapefile support** - Via geopandas/fiona compatibility
- **GeoJSON support** - Import from .geojson files
- **Column mapping** - Interactive mapping of GeoPackage columns to site attributes
- **Automatic coordinate extraction** - Extracts lat/lon from geometry centroids
- **Fallback to fiona** - Works even without geopandas installed
- **Example documentation** - Added geopackage_example.md with sample workflow
- **edges.csv generation** - Automatic network edge generation with Haversine distance calculation
- **Multiple connection types** - Full, distance-based, nearest neighbors, manual
- **Flow calculation** - Automatic flow values inversely proportional to distance

### Changed
- Updated Step 2 (Site Definition) to include GeoPackage import option
- Improved error handling for file imports
- Enhanced documentation with GeoPackage examples
- Updated output to include edges.csv with complete network definition

## [1.0.0] - 2026-04-06

### Added
- Initial release
- 5 built-in compartmental models: SIR, SEIR, SEIS, SIS, SI
- Custom model support
- Interactive 5-step wizard
- Site definition: manual entry, grid layout, city names
- Parameter configuration with validation
- Network connection types: full, distance, neighbors, manual
- Simulation settings configuration
- Output generation: .epg, sites.csv, model_spec.json
- CLI interface

---

## GeoPackage Import Feature

The new GeoPackage import allows users to:

1. **Import real-world spatial data** - Use actual municipal boundaries, health regions, etc.
2. **Automatic coordinate extraction** - No need to manually enter lat/lon
3. **Flexible column mapping** - Map any column names to site attributes
4. **Support large datasets** - Handle thousands of sites at once
5. **Multiple format support** - GeoPackage, Shapefile, GeoJSON via geopandas

### Usage Example

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
