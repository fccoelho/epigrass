# Epigrass Demo Models

This directory contains example epidemiological models demonstrating various features of Epigrass.

## Model Examples

Each subdirectory contains a complete, self-contained example with:
- Model definition file (`.epg`)
- Required data files (CSV, shapefiles)
- README with model description and usage instructions

### Available Models

| Model | Type | Description |
|-------|------|-------------|
| [**flu**](flu/) | Influenza | Influenza model with multiple infectious compartments |
| [**mesh**](mesh/) | SIR | SIR model on a mesh network topology |
| [**rio**](rio/) | SEIR_cont | Rio de Janeiro SEIR continuous model with GIS visualization |
| [**sars**](sars/) | Custom | SARS transmission model |
| [**script**](script/) | Custom | Custom model template/example |
| [**star**](star/) | SIR | SIR model on a star network topology |
| [**vazio**](vazio/) | Template | Empty template for creating new models |
| [**Florida**](Florida/) | SEIR | Florida counties model with GIS and control measures |
| [**ANTT2002**](ANTT2002/) | Data | Brazilian transportation network data resource |

### Additional Resources

- **Notebooks**: Jupyter notebooks for visualization and analysis
- **CustomModel.py**: Example of custom model implementation

## Running a Demo

To run any demo model:

```bash
cd demos/<model_name>
uv run epirunner <model_name>.epg
```

For example, to run the Rio de Janeiro model:

```bash
cd demos/rio
uv run epirunner rio.epg
```

## Creating Your Own Model

1. Start with the empty template:
   ```bash
   cp -r demos/vazio my_model
   cd my_model
   mv vazio.epg my_model.epg
   ```

2. Edit `my_model.epg` to define your model parameters and data files

3. Prepare your data files (sites.csv and edges.csv)

4. Run your model:
   ```bash
   uv run epirunner my_model.epg
   ```

## Network Topologies

Different examples use different network topologies:

- **Star**: Hub-and-spoke network (central node connected to all others)
- **Mesh**: Highly connected network (many interconnections)
- **Geographic**: Real geographic networks (Rio de Janeiro, Florida)

## Model Types

Epigrass supports various epidemiological model types:

- **SIR/SIR_s**: Susceptible-Infected-Recovered
- **SEIR/SEIR_s**: Susceptible-Exposed-Infected-Recovered
- **SEIR_cont**: Continuous-time SEIR model
- **SIS/SIS_s**: Susceptible-Infected-Susceptible
- **Influenza**: Multi-compartment influenza model
- **Custom**: User-defined custom models

## Documentation

For more information, see the [Epigrass Documentation](https://epigrass.readthedocs.io/).
