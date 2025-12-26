.. _gui:

**************************
Gradio Simulation Builder
**************************

Epigrass includes a modern, web-based Graphical User Interface (GUI) built with Gradio. This "Simulation Builder" simplifies the process of creating, configuring, and running simulations by providing an integrated environment for managing simulation files.

Launching the App
=================

To launch the Simulation Builder, use the following command from the project's root directory:

.. code-block:: bash

    uv run epigrass

Once launched, the app will be available in your web browser, typically at ``http://127.0.0.1:7860``.

Core Features
=============

The Simulation Builder is organized into several sections to manage different aspects of your project.

Managing Projects
-----------------

At the top of the interface, you will find options to load or create projects:

* **Load Project**: Select an existing directory containing Epigrass simulation files (.epg, sites.csv, edges.csv).
* **Create New Project**: Initialize a new project directory with template files.
* **Current Project Path**: Displays the absolute path of the project you are currently working on.

Configuration Tabs
------------------

The main body of the app contains several tabs for editing simulation data:

1. **Configuration**: A code editor for the ``.epg`` file. This file defines the epidemiological model, parameters, initial conditions, and simulation settings.
2. **Sites**: An interactive table for editing ``sites.csv``. You can modify site names, populations, coordinates, and other attributes directly.
3. **Edges**: An interactive table for editing ``edges.csv``. This defines the connections between sites, flow rates, and distances.
4. **Map**: If your project includes a shapefile (defined in the ``.epg`` file), this tab will render a geographic map of the study area.

Saving and Running
------------------

* **Save Project**: Saves all changes made in the Configuration, Sites, and Edges tabs back to their respective files in the project directory.
* **Run Simulation**: Executes the Epigrass simulation engine using the current project configuration. The output of the simulation is displayed in the **Status/Output** box at the bottom.

Status and Output
=================

The status box provides real-time feedback on operations like loading, saving, and simulation progress. If a simulation is running, it will display the logs from the simulation engine.
