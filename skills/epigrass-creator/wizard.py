#!/usr/bin/env python3
"""Epigrass Model Creation Wizard - Interactive model builder"""

import json
import os
from datetime import datetime


class EpigrassWizard:
    """Wizard for creating Epigrass epidemiological models"""
    
    MODELS = {
        '1': ('SIR', 'Susceptible-Infectious-Recovered', 'Measles, chickenpox'),
        '2': ('SEIR', 'Susceptible-Exposed-Infectious-Recovered', 'Dengue, COVID-19'),
        '3': ('SEIS', 'Susceptible-Exposed-Infectious-Susceptible', 'Influenza'),
        '4': ('SIS', 'Susceptible-Infectious-Susceptible', 'Common cold'),
        '5': ('SI', 'Susceptible-Infectious', 'HIV/AIDS'),
        '6': ('Custom', 'User-defined', 'Specialized')
    }
    
    def __init__(self):
        self.spec = {
            'model_type': None,
            'sites': [],
            'parameters': {},
            'connections': 'distance',
            'simulation': {'timestep': 1, 'iterations': 365}
        }
    
    def _import_from_geopackage(self, gpkg_path: str) -> bool:
        """Import sites from GeoPackage file"""
        try:
            # Try to import geopandas
            try:
                import geopandas as gpd
            except ImportError:
                print("⚠️  geopandas not installed. Trying with fiona...")
                try:
                    import fiona
                except ImportError:
                    print("✗ Error: Neither geopandas nor fiona is installed.")
                    print("  Install with: pip install geopandas")
                    return False
            
            if not os.path.exists(gpkg_path):
                print(f"✗ File not found: {gpkg_path}")
                return False
            
            print(f"📂 Reading GeoPackage: {gpkg_path}")
            
            # Read with geopandas if available
            if 'gpd' in locals():
                gdf = gpd.read_file(gpkg_path)
            else:
                # Fallback to fiona
                with fiona.open(gpkg_path) as src:
                    gdf = src
            
            print(f"✓ Found {len(gdf)} features")
            print(f"\nAvailable columns: {list(gdf.columns)}")
            
            # Ask user to map columns
            print("\nColumn mapping:")
            name_col = input("  Column for site name [name]: ").strip() or "name"
            pop_col = input("  Column for population [pop/population]: ").strip() or "pop"
            geocode_col = input("  Column for geocode/id [geocode/id]: ").strip() or "geocode"
            
            # Check if columns exist
            available_cols = list(gdf.columns)
            for col in [name_col, pop_col, geocode_col]:
                if col not in available_cols:
                    print(f"⚠️  Warning: Column '{col}' not found in GeoPackage")
                    print(f"   Available: {available_cols}")
            
            # Extract sites
            imported = 0
            for idx, row in gdf.iterrows():
                try:
                    # Get geometry centroid for lat/lon
                    if hasattr(row.geometry, 'centroid'):
                        centroid = row.geometry.centroid
                        lon, lat = centroid.x, centroid.y
                    elif 'lon' in row and 'lat' in row:
                        lon, lat = row['lon'], row['lat']
                    elif 'longitude' in row and 'latitude' in row:
                        lon, lat = row['longitude'], row['latitude']
                    else:
                        lon, lat = 0.0, 0.0
                    
                    site = {
                        'name': str(row.get(name_col, f"Site_{idx}")),
                        'lat': float(lat),
                        'lon': float(lon),
                        'pop': int(row.get(pop_col, 100000)),
                        'geocode': str(row.get(geocode_col, idx + 1))
                    }
                    self.spec['sites'].append(site)
                    imported += 1
                except (ValueError, TypeError) as e:
                    print(f"  ⚠️  Skipped feature {idx}: {e}")
                    continue
            
            print(f"✓ Imported {imported} sites from GeoPackage")
            return True
            
        except Exception as e:
            print(f"✗ Error reading GeoPackage: {e}")
            return False
    
    def step1_model_selection(self):
        """Step 1: Select model type"""
        print("🦠 Step 1/5: Model Selection\n")
        print("| # | Model | Description | Example Diseases |")
        print("|---|-------|-------------|------------------|")
        for k, (name, desc, examples) in self.MODELS.items():
            print(f"| {k} | {name} | {desc} | {examples} |")
        
        choice = input("\nEnter choice (1-6): ").strip()
        if choice in self.MODELS:
            self.spec['model_type'] = self.MODELS[choice][0]
            print(f"✓ Selected: {self.MODELS[choice][0]}\n")
            return True
        return False
    
    def step2_sites(self):
        """Step 2: Define sites"""
        print("🦠 Step 2/5: Define Sites\n")
        print("Options:")
        print("1. Enter city names (manual coordinate entry)")
        print("2. Grid layout (e.g., 5x5)")
        print("3. Manual entry (full data)")
        print("4. Import from GeoPackage (.gpkg)")
        
        option = input("\nChoose option (1-4): ").strip()
        
        if option == '1':
            cities = input("Enter city names (comma-separated): ").strip()
            print("\n⚠️  Note: Using placeholder coordinates (0,0).")
            print("   For accurate coordinates, use GeoPackage import (option 4).")
            for city in cities.split(','):
                self.spec['sites'].append({
                    'name': city.strip(),
                    'lat': 0.0,
                    'lon': 0.0,
                    'pop': 1000000,
                    'geocode': len(self.spec['sites']) + 1
                })
        
        elif option == '2':
            grid = input("Grid size (e.g., 5x5): ").strip()
            try:
                rows, cols = map(int, grid.split('x'))
                for i in range(rows):
                    for j in range(cols):
                        self.spec['sites'].append({
                            'name': f'Node_{i}_{j}',
                            'lat': i * 0.1,
                            'lon': j * 0.1,
                            'pop': 100000,
                            'geocode': i * cols + j + 1
                        })
            except ValueError:
                print("✗ Invalid grid format")
                return False
        
        elif option == '3':
            print("Enter sites (format: Name, Lat, Lon, Pop, Geocode)")
            print("Type 'done' when finished")
            while True:
                line = input("> ").strip()
                if line.lower() == 'done':
                    break
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 5:
                    self.spec['sites'].append({
                        'name': parts[0],
                        'lat': float(parts[1]),
                        'lon': float(parts[2]),
                        'pop': int(parts[3]),
                        'geocode': parts[4]
                    })
        
        elif option == '4':
            gpkg_path = input("Enter GeoPackage file path: ").strip()
            if not self._import_from_geopackage(gpkg_path):
                return False
        
        print(f"✓ Added {len(self.spec['sites'])} sites\n")
        return True
    
    def step3_parameters(self):
        """Step 3: Configure parameters"""
        print("🦠 Step 3/5: Model Parameters\n")
        
        params_help = {
            'beta': 'Transmission rate (0.1-1.0)',
            'gamma': 'Recovery rate = 1/infectious_period_days',
            'alpha': 'Non-linear exponent (1.0 = mass action)',
            'sigma': 'Incubation rate = 1/latent_period_days'
        }
        
        print("Enter parameters (key=value), type 'done' to finish:")
        print(f"Examples: beta=0.4, gamma=0.14 (7-day infectious period)")
        
        while True:
            line = input("> ").strip()
            if line.lower() == 'done':
                break
            if '=' in line:
                key, val = line.split('=', 1)
                try:
                    self.spec['parameters'][key.strip()] = float(val.strip())
                    print(f"  ✓ {key.strip()} = {val.strip()}")
                except ValueError:
                    print(f"  ✗ Invalid value")
        
        print(f"✓ Set {len(self.spec['parameters'])} parameters\n")
        return True
    
    def step4_connections(self):
        """Step 4: Network connections"""
        print("🦠 Step 4/5: Network Connections\n")
        print("1. Fully connected (all sites interact)")
        print("2. Distance-based (closer sites interact more)")
        print("3. Nearest neighbors (N closest)")
        print("4. Manual specification")
        
        choice = input("\nChoose (1-4): ").strip()
        
        if choice == '1':
            self.spec['connections'] = 'full'
        elif choice == '2':
            self.spec['connections'] = 'distance'
        elif choice == '3':
            n = input("Number of neighbors: ").strip()
            self.spec['connections'] = f'neighbors_{n}'
        elif choice == '4':
            self.spec['connections'] = 'manual'
        
        print(f"✓ Connections: {self.spec['connections']}\n")
        return True
    
    def step5_simulation(self):
        """Step 5: Simulation settings"""
        print("🦠 Step 5/5: Simulation Settings\n")
        
        timestep = input("Timestep in days [1]: ").strip() or "1"
        iterations = input("Number of iterations [365]: ").strip() or "365"
        output = input("Output directory [./epigrass_model]: ").strip() or "./epigrass_model"
        
        self.spec['simulation'] = {
            'timestep': int(timestep),
            'iterations': int(iterations),
            'output_dir': output
        }
        
        print(f"✓ Settings saved\n")
        return True
    
    def generate_files(self):
        """Generate all model files"""
        output_dir = self.spec['simulation']['output_dir']
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate .epg script
        script = f"""# Epigrass Model
# Generated: {datetime.now().isoformat()}
# Model: {self.spec['model_type']}

model_type = '{self.spec['model_type']}'
sites_file = 'sites.csv'
edges_file = 'edges.csv'

# Parameters
"""
        for key, val in self.spec['parameters'].items():
            script += f"{key} = {val}\n"
        
        script += f"""
# Simulation
timestep = {self.spec['simulation']['timestep']}
iterations = {self.spec['simulation']['iterations']}
"""
        
        with open(os.path.join(output_dir, 'model.epg'), 'w') as f:
            f.write(script)
        
        # Generate sites.csv
        with open(os.path.join(output_dir, 'sites.csv'), 'w') as f:
            f.write("X,Y,City,Pop,Geocode\n")
            for site in self.spec['sites']:
                f.write(f"{site['lat']},{site['lon']},{site['name']},{site['pop']},{site['geocode']}\n")
        
        # Generate edges.csv
        edges = self._generate_edges()
        with open(os.path.join(output_dir, 'edges.csv'), 'w') as f:
            f.write("Source,Dest,flowSD,flowDS,Distance,geoSource,geoDest\n")
            for edge in edges:
                f.write(f"{edge['source']},{edge['dest']},{edge['flow_sd']},{edge['flow_ds']},{edge['distance']},{edge['geo_source']},{edge['geo_dest']}\n")
        
        # Generate spec.json
        with open(os.path.join(output_dir, 'model_spec.json'), 'w') as f:
            json.dump(self.spec, f, indent=2)
        
        return output_dir
    
    def _generate_edges(self) -> list:
        """Generate edges based on connection type"""
        import math
        
        edges = []
        sites = self.spec['sites']
        connection_type = self.spec['connections']
        
        if connection_type == 'full':
            # Fully connected - all sites connect to all others
            for i, source in enumerate(sites):
                for j, dest in enumerate(sites):
                    if i != j:
                        dist = self._haversine(source['lat'], source['lon'], dest['lat'], dest['lon'])
                        edges.append({
                            'source': source['name'],
                            'dest': dest['name'],
                            'flow_sd': 100,
                            'flow_ds': 100,
                            'distance': round(dist, 2),
                            'geo_source': source['geocode'],
                            'geo_dest': dest['geocode']
                        })
        
        elif connection_type == 'distance':
            # Distance-based - connect if within threshold (default 500km)
            threshold = 500  # km
            for i, source in enumerate(sites):
                for j, dest in enumerate(sites):
                    if i != j:
                        dist = self._haversine(source['lat'], source['lon'], dest['lat'], dest['lon'])
                        if dist <= threshold:
                            edges.append({
                                'source': source['name'],
                                'dest': dest['name'],
                                'flow_sd': max(10, int(1000 / (dist + 1))),
                                'flow_ds': max(10, int(1000 / (dist + 1))),
                                'distance': round(dist, 2),
                                'geo_source': source['geocode'],
                                'geo_dest': dest['geocode']
                            })
        
        elif connection_type.startswith('neighbors_'):
            # Nearest neighbors
            n = int(connection_type.split('_')[1])
            for i, source in enumerate(sites):
                # Calculate distances to all other sites
                distances = []
                for j, dest in enumerate(sites):
                    if i != j:
                        dist = self._haversine(source['lat'], source['lon'], dest['lat'], dest['lon'])
                        distances.append((j, dist, dest))
                
                # Sort by distance and take N closest
                distances.sort(key=lambda x: x[1])
                for j, dist, dest in distances[:n]:
                    edges.append({
                        'source': source['name'],
                        'dest': dest['name'],
                        'flow_sd': max(10, int(1000 / (dist + 1))),
                        'flow_ds': max(10, int(1000 / (dist + 1))),
                        'distance': round(dist, 2),
                        'geo_source': source['geocode'],
                        'geo_dest': dest['geocode']
                    })
        
        elif connection_type == 'manual':
            # Manual - ask user for connections
            print("\nEnter edges manually (format: Source,Dest,FlowSD,FlowDS,Distance)")
            print("Type 'done' when finished, or 'auto' for automatic generation")
            
            while True:
                line = input("> ").strip()
                if line.lower() == 'done':
                    break
                if line.lower() == 'auto':
                    # Auto-generate distance-based edges
                    return self._generate_edges_with_type('distance')
                
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 5:
                    edges.append({
                        'source': parts[0],
                        'dest': parts[1],
                        'flow_sd': int(parts[2]),
                        'flow_ds': int(parts[3]),
                        'distance': float(parts[4]),
                        'geo_source': parts[0],
                        'geo_dest': parts[1]
                    })
        
        return edges
    
    def _generate_edges_with_type(self, conn_type: str) -> list:
        """Generate edges with a specific connection type"""
        original = self.spec['connections']
        self.spec['connections'] = conn_type
        edges = self._generate_edges()
        self.spec['connections'] = original
        return edges
    
    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in km using Haversine formula"""
        import math
        
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def run(self):
        """Run the complete wizard"""
        print("=" * 50)
        print("🦠 Epigrass Model Creation Wizard")
        print("=" * 50)
        print()
        
        steps = [
            self.step1_model_selection,
            self.step2_sites,
            self.step3_parameters,
            self.step4_connections,
            self.step5_simulation
        ]
        
        for step in steps:
            if not step():
                print("✗ Wizard cancelled")
                return None
        
        # Generate files
        output_dir = self.generate_files()
        
        # Count edges
        num_edges = len(self._generate_edges())
        
        # Summary
        print("=" * 50)
        print("✅ Model Created Successfully!")
        print("=" * 50)
        print(f"\nModel Type: {self.spec['model_type']}")
        print(f"Sites: {len(self.spec['sites'])}")
        print(f"Edges: {num_edges}")
        print(f"Parameters: {list(self.spec['parameters'].keys())}")
        print(f"\nFiles generated in: {output_dir}/")
        print("  - model.epg")
        print("  - sites.csv")
        print("  - edges.csv")
        print("  - model_spec.json")
        print(f"\nTo run: cd {output_dir} && epirunner model.epg")
        
        return output_dir


if __name__ == '__main__':
    wizard = EpigrassWizard()
    wizard.run()
