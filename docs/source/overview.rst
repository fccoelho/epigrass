********************
Overview of Epigrass
********************
Epigrass is a platform for network epidemiological simulation and analysis. It enables researchers to perform comprehensive spatio-temporal simulations incorporating epidemiological data and models for disease transmission and control in order to create sophisticated scenario analyses.



Modeling Approach
=================

The geographical networks  over which epidemiological processes take place can be very straightforwardly represented in a object-oriented framework. In such a framework, the nodes and edges of the geographical networks are objects with their attributes and methods.

Once the archetypal node and edge objects are defined with appropriate attributes and methods, then a code representation of the real system can be constructed, where cities (or other geographical localities) and transportation routes are instances of the node and edge objects, respectively. The whole network is also an object with a whole collection of attributes and methods.

This framework leads to a compact and hierarchical computational model consisting of a network object containing a variable number of node and edge objects. This framework also do not pose limitations to encapsulation, potentially allowing for networks within networks if desirable.

For the end user perspective, this framework is transparent since it mimics the natural structure of the real system. Even after the model is converted into a code object all of its component objects remain accessible to the user's  models.

Geographical Network Models
===========================

.. index:: shapefile

Epigrass's geo-referenced models are built from two basic sources of data: a map (in shapefile format) which provide the cartographical base over which the models are represented and specific data about nodes and edges that are provided by the user for the network of interest.

Defining the Cartographic Background
------------------------------------

If the user has a map for the georeferred data, this can be passed to Epigrass. In this case, the cartographic background is defined by defining the name of the shapefile file (with path relative to the working directory) in the model'.epg file. Along with the path to the shapefile,  the variable in the shapefile, which contains the geocode of localities and their name must also be specified::

    shapefile =  ['riozonas_LatLong.shp','nome_zonas','zona_trafe']

If the user does not have a map in shapefile format, he can still use Epigrass. In this case, the georeferred data is read only from two .csv files (more on that ahead).

.. index:: node, site

Defining Nodes
--------------

A graph has nodes and edges. Nodes can be cities or other localities depending on the model being constructed. The definition of nodes require the setting of many attributes listed below. The nodes will have many more attributes defined at run-time which will depend on other aspects of the model, these will be discussed later.

The data necessary at build time to create nodes come from a CSV (comma-separated-values) ASCII-text file, with the following attributes, (in this order):

*Latitude, Longitude*
    This attribute will be used to geo reference the  node. The coordinate system must match those used in the cartographic base imported from GRASS. Coordinates can be coded in either decimal or sexagesimal format.
*Name*
    Used for identification purposes only. It can be a city name, for instance.
*Population*
    Since the simulation models will all be of a populational nature. Population size must be specified at build time.
*Geocode*
    A Unique Geocode (a number) is required. It will be used as a label/index to facilitate  reference to specific nodes.

.. index:: edge

Defining Edges
--------------

In Epigrass' graphs, edges represent transportation routes. Similarly to nodes, edges are defined at build-time with a reduced set of attributes which will be extended at run-time. Epigrass also expects to get these attributes from a CSV file:


*Source*
    The name of the source node. The edges are bi-directional, but the nodes are labeled source and destination for reference purposes.
*Destination*
    The name of the destination node.
*Forward migration*
    Migration rate from source to destination, in number of persons per unit of time.
*Backward migration*
    Migration rate from destination to source, in number of persons per unit of time.
*Length*
    Distance in kilometers (or another unit) from source to destination via the particular route (not straight line distance).
*Source's geocode*
    This is the unique numerical identifier used in the sites file.
*Destination's geocode*
    This is the unique numerical identifier used in the sites file.


.. index:: models

Defining models
---------------

The word model in Epigrass can mean two distinct objects: The network model and the node's epidemic model.

Node objects, in an Epigrass model, contain well-mixed population dynamic models within them. These models determine the dynamics of epidemics within the particular environments of each node. Epigrass comes with a few standard epidemiological models\index{Models!epidemiological models} to choose from when setting up your network. Currently, The same model type is applied to every node although their parameterization is node-specific. Besides the built-in model types, users can define their own, as shown in the chapter *Using Epigrass*.

.. index::
    single: models;epidemiological models
	single: models;network models

Network models are specified in a ASCII-text script file (Called a :file:`.epg` file). Epigrass comes with a few demo Network models for the user to play with until he/she is confident enough to build their own. Even then, it is advisable to use the demo scripts provided as templates to minimize syntax errors.

The script on the appendix  specifies a network model with an stochastic SEIR (see chapter on epidemiological modeling) epidemic model in its nodes. The user should study this model and play with its parameters to understand the features of Epigrass. A step-by-step tutorial on how to edit the model script can be found in the chapter *Using Epigrass*.

The Simulation
==============

A simulation run in Epigrass consists of a series of tasks performed at each time step [#]_ .

*Calculate migration*
    For all edges in the network, the number of persons traveling each way is determined for the current time-step.
*Run epidemic models*
    For each node in the network the epidemic demographics are updated based on the local number of infected and susceptible individuals which have been updated by the transportation system.


All aspects of the simulation such as number of passengers traveling on each edge, number of infected/susceptible on each node and etc., are recorded in a step-by-step basis. This complete record allows for the model to be analyzed after the simulation has been completed without having to recalculate it.


Output
------
The output of a simulation in Epigrass is three-fold: A graphical display which the animated outcome of the simulation,  a written report, and a database table with numeric results.

Graphical display
^^^^^^^^^^^^^^^^^

During a simulation, selected epidemiological variables are animated in a 3-dimensional rendering over the map of the region containing the network.

Report Generation
^^^^^^^^^^^^^^^^^

The report contains a detailed analysis of the network model and the simulations ran with it. The report generates a \LaTeX source file and compiles it to a PDF document for visualization.

Three types of report are currently available:

**Report = 1**
    Returns a set of descriptors of the network, described in chapter
**Report = 2**
    Returns a set of basic epidemiological measures and plots of the time series.
**Report = 3**
    Report 1 + Report 2


Report Generation is an optional, though recommended, step done at the end of the simulation. For the report, descriptive statistics are generated for the network. These have to do with network topology and properties. Additional sections can be added to the report with basic statistical analyses of the output of pre-selected nodes [#]_ .

Database output
^^^^^^^^^^^^^^^
.. index::
    single: Database;results table
    single: Database;epigrass database

Time series of **L**, **S**, **E**, and **I**, from simulations, are stored in a MySQL database named *epigrass* . The results of each individual simulation is stored in a different table named after the model's script name, the date and time the simulation has been run. For instance, suppose you run a simulation of a model stored in a file named :file:`script.epg`, then at the end of the simulation, a new table in the epigrass database will be created with the following name: *script\_Wed\_Jan\_26\_154411\_2005*. Thus, the results of multiple runs from the same model get stored independently.

Epigrass also supports the SQLite database and CSV files as output for the time-series. The naming convention also applies to these other formats.


.. rubric:: Footnotes

.. [#] The number of time steps is defined in the model script
.. [#] Listed in the siteRep variable at the script
