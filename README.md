# Epigrass
If you use epigrass in your research, please use the following DOI to cite it:

[![DOI](https://zenodo.org/badge/59497476.svg)](https://zenodo.org/badge/latestdoi/59497476)
or this bibtex entry.
```bibtex
@software{flavio_codeco_coelho_2021_4554753,
  author       = {Flávio Codeço Coelho},
  title        = {fccoelho/epigrass: COVID19},
  month        = feb,
  year         = 2021,
  publisher    = {Zenodo},
  version      = {v3.0.2},
  doi          = {10.5281/zenodo.4554753},
  url          = {https://doi.org/10.5281/zenodo.4554753}
}
```
## Epidemiological Geo-referenced Analysis and Simulation system
![dashboard](docs/source/dashboard2.png)
Epigrass is a Python Library aimed at making the simulation of metapopulation models as easy as possible.
Documentation is available [here](https://epigrass.readthedocs.io/en/latest/).

## Installation
### External dependencies
Besides installing epigrass from the PyPI, as described below you will need to install the following external dependencies:
- redis server you need to have a redis server running. You can install it from the [redis website](https://redis.io/download)  
- 
You can install Epigrass directly from PyPI, the Python Package Index.
For mode details, check the [docs](https://epigrass.readthedocs.io/en/latest/install.html#)

## Installing from the repository
If you clone the repository, you can install Epigrass with the following command:
```bash
$ uv sync
```

## Running the Gradio Simulation Builder
Epigrass now includes a modern web-based simulation builder built with Gradio. This interface allows you to create, edit, and run simulations easily.

To launch the simulation builder:
```bash
$ uv run epigrass
```
This will start a local web server and provide a URL (usually `http://127.0.0.1:7860`) where you can access the interface.

## Running demos
The source distribution comes with a few demos.
```bash
$ cd demos
$ uv run epirunner rio.epg
```
This will run the demo for the city of Rio de Janeiro. 

## Getting started building your own models

Folow [these instructions](https://epigrass.readthedocs.io/en/latest/using.html).
