#!/usr/bin/env python3
"""
Epigrass Model Creation Wizard

Interactive step-by-step wizard for creating Epigrass epidemiological models.
Supports built-in models (SIR, SEIR, SEIS, SIS, SI) and custom models.
"""

import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class EpigrassWizard:
    """Interactive wizard for creating Epigrass models"""
    
    BUILTIN_MODELS = {
        'SIR': {
            'name': 'SIR',
            'description': 'Susceptible-Infectious-Recovered',
            'compartments': ['Susceptible', 'Infectious', 'Recovered'],
            'parameters': ['beta', 'alpha', 'gamma', 'delta'],
            'use_case': 'Diseases with lifelong immunity'
        },
        'SEIR': {
            'name': 'SEIR',
            'description': 'Susceptible-Exposed-Infectious-Recovered',
            'compartments': ['Susceptible', 'Exposed', 'Infectious', 'Recovered'],
            'parameters': ['beta', 'alpha', 'sigma', 'gamma', 'delta'],
            'use_case': 'Diseases with latent/incubation period'
        },
        'SEIS': {
            'name': 'SEIS',
            'description': 'Susceptible-Exposed-Infectious-Susceptible',
            'compartments': ['Susceptible', 'Exposed', 'Infectious'],
            'parameters': ['beta', 'alpha', 'sigma', 'gamma', 'delta'],
            'use_case': 'Diseases with temporary immunity'
        },
        'SIS': {
            'name': 'SIS',
            'description': 'Susceptible-Infectious-Susceptible',
            'compartments': ['Susceptible', 'Infectious'],
            'parameters': ['beta', 'alpha', 'gamma', 'delta'],
            'use_case': 'Diseases with no immunity'
        },
        'SI': {
            'name': 'SI',
            'description': 'Susceptible-Infectious',
            'compartments': ['Susceptible', 'Infectious'],
            'parameters': ['beta', 'alpha', 'gamma'],
            'use_case': 'Fatal diseases (no recovery)'
        }
    }
    
    def __init__(self):
        self.model_spec = {
            'model_type': None,
            'model_name': None,
            'sites': [],
            'edges': [],
            'parameters': {},
            'simulation': {},
            'output_dir': './epigrass_output'
        }
        self.current_step = 0
        
    def get_model_selection_prompt(self) -> str:
        """Generate model selection prompt"""
        prompt = """🦠 **Epigrass Model Creation Wizard**

**Step 1: Select Model Type**

Choose an epidemiological model for your simulation:

| # | Model | Description | Best For |
|---|-------|-------------|----------|"""
        
        for idx, (key, model) in enumerate(self.BUILTIN_MODELS.items(), 1):
            prompt += f"\n| {idx} | {key} | {model['description']} | {model['use_case']} |"
        
        prompt += """\n| 6 | Custom | User-defined model | Specialized scenarios |

**Enter your choice (1-6):**"""
        
        return prompt
    
    def set_model_type(self, choice: str) -> bool:
        """Set model type based on user choice"""
        models = list(self.BUILTIN_MODELS.keys())
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(models):
                self.model_spec['model_type'] = models[idx]
                self.model_spec['model_name'] = models[idx]
                return True
            elif idx == len(models):  # Custom
                self.model_spec['model_type'] = 'Custom'
                return True
        except ValueError:
            pass
        
        return False
    
    def get_sites_prompt(self) -> str:
        """Generate sites definition prompt"""
        return """**Step 2: Define Network Sites**

Sites are geographic locations (cities, neighborhoods) in your model.

**Option 1: Manual Entry**
Enter sites one by one with format:
`Name, Latitude, Longitude, Population, Geocode`

Example:
```
Sao_Paulo, -23.5505, -46.6333, 12300000, 3550308
Rio_de_Janeiro, -22.9068, -43.1729, 6750000, 3304557
```

**Option 2: Brazilian Cities**
Provide list of city names (I'll fetch coordinates and populations):
```
São Paulo, Rio de Janeiro, Belo Horizonte, Salvador
```

**Option 3: Grid Layout**
Specify grid dimensions for synthetic network:
```
grid: 5x5 (25 sites)
```

**Enter your sites (or type 'done' to finish):**"""
    
    def add_site(self, site_data: str) -> bool:
        """Add a site to the model"""
        if site_data.lower() == 'done':
            return True
            
        try:
            parts = [p.strip() for p in site_data.split(',')]
            if len(parts) >= 5:
                site = {
                    'name': parts[0],
                    'lat': float(parts[1]),
                    'lon': float(parts[2]),
                    'population': int(parts[3]),
                    'geocode': parts[4]
                }
                self.model_spec['sites'].append(site)
                return True
            elif len(parts) >= 2 and parts[0].lower().startswith('grid:'):
                # Handle grid creation
                return self._create_grid_sites(parts[0])
        except (ValueError, IndexError):
            pass
        
        return False
    
    def _create_grid_sites(self, grid_spec: str) -> bool:
        """Create synthetic grid of sites"""
        try:
            dims = grid_spec.split(':')[1].strip().split('x')
            rows, cols = int(dims[0]), int(dims[1])
            
            for i in range(rows):
                for j in range(cols):
                    site = {
                        'name': f'Node_{i}_{j}',
                        'lat': i * 0.1,
                        'lon': j * 0.1,
                        'population': 100000,
                        'geocode': i * cols + j + 1
                    }
                    self.model_spec['sites'].append(site)
            return True
        except (ValueError, IndexError):
            return False
    
    def get_parameters_prompt(self) -> str:
        """Generate parameters configuration prompt"""
        model_type = self.model_spec['model_type']
        
        if model_type == 'Custom':
            return self._get_custom_model_prompt()
        
        model = self.BUILTIN_MODELS.get(model_type)
        if not model:
            return "Error: Model not selected"
        
        prompt = f"""**Step 3: Configure Model Parameters**

**Selected Model: {model_type}**
Compartments: {', '.join(model['compartments'])}

**Parameter Definitions:**
- **beta (β)**: Transmission rate (contact rate × probability of transmission)
  - Typical range: 0.1 - 1.0
  
- **alpha (α)**: Non-linear transmission exponent
  - 1.0 = mass action, < 1.0 = saturating transmission
  
- **gamma (γ)**: Recovery rate (1 / infectious period in days)
  - For 7-day infectious period: γ = 0.14
  
- **delta (δ)**: Immunity loss rate (0 = permanent immunity)
  
- **sigma (σ)**: Incubation rate (1 / latent period) - for SEIR/SEIS
  - For 5-day incubation: σ = 0.2

**Enter parameters as key=value pairs (one per line):**
```
beta=0.5
gamma=0.14
```

**Type 'done' when finished:**"""
        
        return prompt
    
    def _get_custom_model_prompt(self) -> str:
        """Generate custom model prompt"""
        return """**Step 3: Define Custom Model**

Create your own compartmental model by specifying:

1. **Compartment Names** (comma-separated):
   ```
   Susceptible, Exposed, Infectious, Hospitalized, Recovered, Dead
   ```

2. **Transitions** (one per line, format: From -> To: rate):
   ```
   Susceptible -> Exposed: beta*I/N
   Exposed -> Infectious: sigma
   Infectious -> Hospitalized: rho
   Infectious -> Recovered: gamma*(1-rho)
   Hospitalized -> Recovered: gamma_h
   Hospitalized -> Dead: mu
   ```

3. **Initial Conditions** (for each compartment):
   ```
   S: 0.999, E: 0.0, I: 0.001, H: 0.0, R: 0.0, D: 0.0
   ```

**Enter compartment names first:**"""
    
    def add_parameter(self, param_line: str) -> bool:
        """Add a parameter to the model"""
        if param_line.lower() == 'done':
            return True
            
        try:
            if '=' in param_line:
                key, value = param_line.split('=', 1)
                self.model_spec['parameters'][key.strip()] = float(value.strip())
                return True
        except ValueError:
            pass
        
        return False
    
    def get_edges_prompt(self) -> str:
        """Generate edges/connections prompt"""
        num_sites = len(self.model_spec['sites'])
        
        return f"""**Step 4: Define Network Connections (Edges)**

You have {num_sites} sites defined.

**Connection Options:**

**Option 1: Fully Connected** (all sites connected)
```
full: distance_based
```

**Option 2: Nearest Neighbors** (connect to N closest)
```
neighbors: 4
```

**Option 3: Distance Threshold** (connect if within distance)
```
distance: 100 (km)
```

**Option 4: Manual Entry** (format: Source, Dest, Flow_SD, Flow_DS, Distance)
```
Sao_Paulo, Rio_de_Janeiro, 1000, 1000, 400
```

**Option 5: Commuting Matrix** (provide origin-destination flow data)

**Enter connections:**"""
    
    def get_simulation_prompt(self) -> str:
        """Generate simulation settings prompt"""
        return """**Step 5: Simulation Settings**

Configure the simulation run:

**Time Settings:**
- **Timestep**: Duration of each step (days)
  ```
  timestep: 1 (daily)
  ```

- **Iterations**: Number of time steps to simulate
  ```
  iterations: 365 (1 year)
  ```

**Output Settings:**
- **Output directory**: Where to save results
  ```
  output_dir: ./results
  ```

- **Visualizations**: What outputs to generate
  ```
  maps: yes
  timeseries: yes
  network: yes
  ```

**Enter settings (key=value, one per line, 'done' to finish):**
```
timestep=1
iterations=365
```"""
    
    def add_simulation_setting(self, setting: str) -> bool:
        """Add simulation setting"""
        if setting.lower() == 'done':
            return True
            
        try:
            if '=' in setting:
                key, value = setting.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Try to convert to appropriate type
                if value.lower() in ('yes', 'true'):
                    value = True
                elif value.lower() in ('no', 'false'):
                    value = False
                else:
                    try:
                        value = int(value)
                    except ValueError:
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                
                self.model_spec['simulation'][key] = value
                return True
        except ValueError:
            pass
        
        return False
    
    def generate_epg_script(self) -> str:
        """Generate the .epg script file"""
        model_type = self.model_spec['model_type']
        
        script = f"""# Epigrass Model Script
# Generated: {datetime.now().isoformat()}
# Model Type: {model_type}

# Model Configuration
model_type = '{model_type}'
model_name = '{self.model_spec.get('model_name', 'MyModel')}'

# Sites file
sites_file = 'sites.csv'

# Edges file  
edges_file = 'edges.csv'

# Simulation parameters
"""
        
        # Add model-specific parameters
        for key, value in self.model_spec['parameters'].items():
            script += f"{key} = {value}\n"
        
        # Add simulation settings
        script += "\n# Simulation settings\n"
        for key, value in self.model_spec['simulation'].items():
            if isinstance(value, str):
                script += f"{key} = '{value}'\n"
            else:
                script += f"{key} = {value}\n"
        
        return script
    
    def generate_sites_csv(self) -> str:
        """Generate sites CSV content"""
        if not self.model_spec['sites']:
            return ""
        
        output = "# Sites data for Epigrass model\n"
        output += "X,Y,City,Pop,Geocode\n"
        
        for site in self.model_spec['sites']:
            output += f"{site['lat']},{site['lon']},{site['name']},{site['population']},{site['geocode']}\n"
        
        return output
    
    def save_model(self, output_dir: str = './epigrass_model'):
        """Save all model files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save .epg script
        script_path = os.path.join(output_dir, 'model.epg')
        with open(script_path, 'w') as f:
            f.write(self.generate_epg_script())
        
        # Save sites CSV
        sites_path = os.path.join(output_dir, 'sites.csv')
        with open(sites_path, 'w') as f:
            f.write(self.generate_sites_csv())
        
        # Save specification JSON
        spec_path = os.path.join(output_dir, 'model_spec.json')
        with open(spec_path, 'w') as f:
            json.dump(self.model_spec, f, indent=2)
        
        return output_dir
    
    def get_summary(self) -> str:
        """Generate model summary"""
        summary = f"""📊 **Model Summary**

**Model Type:** {self.model_spec['model_type']}
**Number of Sites:** {len(self.model_spec['sites'])}
**Number of Edges:** {len(self.model_spec['edges'])}

**Parameters:**
"""
        for key, value in self.model_spec['parameters'].items():
            summary += f"  - {key}: {value}\n"
        
        summary += f"\n**Simulation Settings:**\n"
        for key, value in self.model_spec['simulation'].items():
            summary += f"  - {key}: {value}\n"
        
        summary += """
**Files Generated:**
- model.epg (Epigrass script)
- sites.csv (Site data)
- model_spec.json (Full specification)

**To run the simulation:**
```bash
cd epigrass_model
epirunner model.epg
```
"""
        
        return summary


def main():
    """Main entry point for CLI usage"""
    import sys
    
    wizard = EpigrassWizard()
    
    print("🦠 Epigrass Model Creation Wizard")
    print("=" * 50)
    print()
    
    # Step 1: Model selection
    print(wizard.get_model_selection_prompt())
    while True:
        choice = input("\n> ")
        if wizard.set_model_type(choice):
            print(f"✓ Selected: {wizard.model_spec['model_type']}")
            break
        print("✗ Invalid choice. Please enter 1-6.")
    
    # Step 2: Sites
    print("\n" + wizard.get_sites_prompt())
    while True:
        site_data = input("> ")
        if wizard.add_site(site_data) and site_data.lower() == 'done':
            break
        if site_data.lower() != 'done':
            print(f"✓ Added site. Total: {len(wizard.model_spec['sites'])}")
    
    print(f"✓ Defined {len(wizard.model_spec['sites'])} sites")
    
    # Step 3: Parameters
    print("\n" + wizard.get_parameters_prompt())
    while True:
        param = input("> ")
        if wizard.add_parameter(param) and param.lower() == 'done':
            break
        if param.lower() != 'done':
            print(f"✓ Added parameter")
    
    # Step 4: Simulation settings
    print("\n" + wizard.get_simulation_prompt())
    while True:
        setting = input("> ")
        if wizard.add_simulation_setting(setting) and setting.lower() == 'done':
            break
        if setting.lower() != 'done':
            print(f"✓ Added setting")
    
    # Generate and save
    output_dir = wizard.save_model()
    
    print("\n" + "=" * 50)
    print(wizard.get_summary())
    print(f"\n✓ Model saved to: {output_dir}/")


if __name__ == '__main__':
    main()
