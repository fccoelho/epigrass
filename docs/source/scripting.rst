.. _custom:

*********************
Writing Custom Models
*********************

.. index:: custom models

The most powerful feature of Epigrass is the ability to use custom
models. It allows the user to specify intra-node dynamics and, in
doing so, break away from the limitations imposed by the built-in
models. 

By learning to write his/her own models, the user begins to realize
the full potential of Epigrass, which goes beyond being a platform to
simulate networked epidemics. In reality Epigrass can be used to model
any distributed dynamical system taking place on a set of nodes
(connected or not).


Getting Started
===============

The best way to get started in writing custom models is to look at the
example distributed with Epigrass. It can be found in 
:file:`demos/CustomModel_example.py`::

	# This is a custom model to used in place of Epigrass' built-in models. Custom
	# models must always be on a file named CustomModel.py and contain at least 
	# a function named Model. Both the File name and the function Names are case-sensitive,
	# so be careful. Please refer to the manual for intructions on how to write your 
	# own custom models.

	def Model(self,vars,par,theta=0, npass=0):
		"""
		Calculates the model SIR, and return its values.
		* vars The state variables of the models
		* par  The parameters (Beta, alpha, E,r,delta,B, w, p) see docs.
		* theta = infectious individuals from neighbor sites
		* npass = Total number of people arriving at this node
		"""
		# Get state variables' current values

		if self.parentSite.parentGraph.simstep == 1:  # if first step
			# Define variable names to appear in the output
			self.parentSite.vnames = ('Exposed','Infectious','Susceptible')
			# And get state variables's initial values (stored in dict self.bi)
			
			E,I,S = (self.bi['e'],self.bi['i'],self.bi['s'])
		else:   # if nor first step
			E,I,S = vars

		# Get parameter values	
		N = self.parentSite.totpop
		beta,alpha,e,r,delta,B,w,p = (self.bp['beta'],self.bp['alpha'],
		self.bp['e'],self.bp['r'],self.bp['delta'],self.bp['b'],
		self.bp['w'],self.bp['p'])

		#Vacination event (optional)
		if self.parentSite.vaccineNow:
			S -= self.parentSite.vaccov*S
		
		# Model
		Lpos = beta*S*((I+theta)/(N+npass))**alpha #Number of new cases
		Ipos = (1-r)*I + Lpos
		Spos = S + B - Lpos
		Rpos = N-(Spos+Ipos)
		
		# Update stats
		self.parentSite.totalcases += Lpos #update number of cases
		self.parentSite.incidence.append(Lpos)

		# Raise site infected flag and add parent site to the epidemic history list.
		if not self.parentSite.infected: 
			if Lpos > 0:
				self.parentSite.infected = self.parentSite.parentGraph.simstep
				self.parentSite.parentGraph.epipath.append(
				(self.parentSite.parentGraph.simstep,
				self.parentSite,self.parentSite.infector))
		
		self.parentSite.migInf.append(Ipos)
			
		return [0,Ipos,Spos]

Let's analyze the above code. The first thing to notice is that an Epigrass custom model is a Python program. So anything you can do with Python in your system, you can do in your custom model. Naturally, your knowledge of the Python programming language will define how far you can go in this customization. There are a few requirements on this Python program in order to make it a valid custom model from Epigrass's perspective. 

#. It must define a global function named **Model**. This function will be inserted as a method on every node object, at run time.
	#. This function must declare the following arguments:
		* *self*: reference to the model object.
		* *vars*: A list with the values of the model's state variables in time t-1 in the same order as returned by this function.
		* *par*: The parameters of the model. Listed in the same order as defined in the :file:`.epg` file.
		* *theta*: Number of infectious individuals arriving from neighboring sites. For disconnected models, it is 0.
		* *npass*: The total number of passengers arriving from neighboring sites. For disconnected models, it is 0.
	#. In the beginning of the function you define a list of strings (self.parentSite.vnames) which will be the names used when storing the resulting time-series in the database. Choose strings that are not very long and are meaningful. You only need to do this once, ate the beginning of the simulation so put it inside an *if* statement, which will be executed only at time-step 1 (see code above).
	#. After defining variable names, set their initial values in the same *if* clause. An *else* clause linked to this one will set variables values for the rest of the simulation.
	#. Define local names for the total population *N* and fixed parameters.
	#. Proceed to implement your model anyway you see fit.
	#. Feed some site level variables (*incidence*,) with the result of the simulation.
		* *incidence*: list of new cases per time step.
		* *infected*: Boolean stating if the site has been infected, i.e., it has had an autoctonous case.
		* *epipath*: This variable is at the graph level and contains the path of spread of the simulation.
		* *migInf*: Number of infectious individuals in this site per time-step.
	#. Finally, this function must return a list/tuple with the values of the state variables in the same order as received in vars.

  .. warning::

	The strings in self.parentSite.vnames must be valid *SQL* variable names, or else you will have a insert error at the end of the simulation. 

After defining this function with all its required features, you can continue to develop you custom model, writing other functions classes, etc. Note however, that only the *Model* function will be called by Epigrass, so any other code you add to your program must be called from within that function.

.. note::

	Since :file:`CustomModel` is imported from within Epigrass, any global code (unindented) in it is also  executed. So you may add imports and other initialization code.

.. warning::

	The name CustomModel.py is case-sensitive and cannot be changed. The same is true for the *Model* function.

The Environment
===============

.. figure:: Diagrama1.png
	
	Nesting of the objects inside a Simulate object.

From quickly going through the example Custom model above it probably became clear, to the Python-initiated, that Yous can access variables at the node and graph levels.  This is possible because *Model* becomes a method in a node object which in is turn is contained into a graph object (see figure).

Besides being nested within the *graph* object, *node* and *edge* contain references to their containers. This means that using the introspective abilities of Python the user can access any information at any level of the full *graph* model and use it in the custom model. In order to help you do this, Let's establish an API for developing custom models.

Model Development API
---------------------

All attributes and methods (functions) from all around the simulation must be references from the model's  perspective, denoted by *self*. The parent objects can be accessed through the following notation:

* *self.parentSite*
	Is the Site (node) containing the model. 
* *self.parentSite.parentGraph*
	Is the Graph containing the parent site of the model.

The following attributes and methods can be accessed by appending them to one one the objects above. For example::

	self.parentSite.parentGraph.simstep

Site Attributes and Methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Not all attributes and methods are listed, only the most useful. For a complete reference, look at the source code documentation.

.. class:: Site

	self.parentSite. Actually named *siteobj* in the source code.

	.. attribute:: bi

		Dictionary with initial values for all of the model's state variables. Keys are the variable names.
	
	.. attribute:: bp

		Dictionary with initial values for all of the model's parameters. Keys are the parameter names.

	.. attribute:: totpop

		Initial total population

	.. attribute:: ts

		List containing the model output time series (variables in the same order of the model)

 	.. attribute:: incidence

		Incidence time series 

 	.. attribute:: infected

		Has the site been already infected? (logical variable)

 	.. attribute:: sitename

		Site's name (provided in the .csv)

  	.. attribute:: values

		Tuple containing extra-variables provided by .csv file

	.. attribute:: parentGraph

		Graph to which Site belongs (see class Graph) 

	.. attribute:: edges

		List containing all edge objects connected to Site

	.. attribute:: inedges

		List containing all inbound edges

	.. attribute:: outedges

		List containing all outbound edges

	.. attribute:: geocode

		Site's geocode

	.. attribute:: modtype

		Type of dynamic model running in Site
		
	.. attribute:: vaccination

		Time and coverage of vaccination event. Format as in .epg

	.. attribute:: vaccineNow

		Flag indicating that it is vaccine day (0 or 1)

	.. attribute:: vaccov

		Current vaccination coverage

	.. method:: vaccinate(cov)

		At time t, the population is vaccinated with coverage cov

	.. method:: getOutEdges()

		Returns list of outbound edges

	.. method:: getInEdges()

		Returns list of inbound edges

	.. method:: getNeighbors()

		Returns a dictionary of neighbor sites as keys and distances as values

	.. method:: getDistanceFromNeighbor(site)

		Returns the distance in km from a given neighbor

	.. method:: getDegree(site)

		Returns degree of this site, that is, the number of sites connected to it

	


Graph Attributes and Methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Not all attributes and methods are listed, only the most useful. For a complete reference, look at the source code documentation.

.. class:: Graph

	self.parentSite.parentGraph

	.. attribute:: simstep

		Time-step of the simulation. Use it to keep track of the simulation progress.
		
	.. attribute:: speed

		The speed of the transportation system

	.. attribute:: maxstep

		Final time-step of the simulation

	.. attribute:: episize

		Current size of the epidemic, graph-wise.

	.. attribute:: site_list

		Full list of nodes in the graph. Each element in this list is a real node object.

	.. attribute:: edge_list

		Full list of nodes in the graph. Each element in this list is a real node object.

	.. method:: getSite(name)

		Returns an site object named *name*



