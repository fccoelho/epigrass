# Empty Template

## Overview
This is an **empty template file** for creating new Epigrass models. Use this as a starting point for defining your own epidemiological models.

## Usage
1. Copy `vazio.epg` to your working directory
2. Rename it to your model name (e.g., `my_model.epg`)
3. Edit the file to add your model configuration

## Sections to Define
A complete .epg file should include the following sections:

### [THE WORLD]
Define the network topology:
- `shapefile`: Geographic shapefile for visualization (optional)
- `sites`: CSV file with site/population data
- `edges`: CSV file with network connectivity
- `encoding`: Character encoding for CSV files

### [EPIDEMIOLOGICAL MODEL]
Choose your model type:
- SIS, SIS_s, SIR, SIR_s, SEIS, SEIS_s, SEIR, SEIR_s
- SIpRpS, SIpRpS_s, SIpR, SIpR_s
- Influenza
- Custom (for user-defined models)

### [MODEL PARAMETERS]
Define epidemiological parameters:
- `beta`: Transmission coefficient
- `alpha`: Clumping parameter
- `e`: Inverse of incubation period
- `r`: Inverse of infectious period
- `delta`: Probability of acquiring immunity
- `B`: Birth rate
- `w`: Probability of immunity waning
- `p`: Probability of reinfection

### [INITIAL CONDITIONS]
Set initial epidemiological states:
- `S`: Susceptible population
- `E`: Exposed population (for SE models)
- `I`: Infected population
- `R`: Recovered population (for SIR/SEIR models)

### [EVENTS]
Define site-specific events or interventions (optional)

### [SIMULATION]
Configure simulation parameters:
- `report`: Reporting frequency
- `loop`: Number of simulation runs

## Getting Started
```bash
# Copy the template
cp demos/vazio/vazio.epg my_model.epg

# Edit with your favorite text editor
nano my_model.epg

# Run your model
uv run epirunner my_model.epg
```

## Resources
- [Epigrass Documentation](https://epigrass.readthedocs.io/)
- [Model Types Reference](https://epigrass.readthedocs.io/en/latest/models.html)
- [Tutorial](https://epigrass.readthedocs.io/en/latest/using.html)
