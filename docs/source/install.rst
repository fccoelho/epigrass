.. _install:

***********************
Building and Installing
***********************

This chapter will walk through all aspects of Epigrass installation. From obtaining, building and installing  the prerequisites to the installation of Epigrass itself.

Most of the steps will be quite simple and similar since they will make use of standard tools for package installation on Debian GNU/Linux and derivatives. If you use a different distribution, you should check its documentation for package installation instructions.

If, on your distribution, a package is not available for the required version, you can try to obtain an updated version of the package at the web-sites provided. On the rare cases where pre-built packages are not available, instructions on how to build the software from source should also be available from its web-site.

Required Packages
=================

Python
------


*Web-site:*
    http://www.python.org
*Version required:*
    >= 2.5 < 3


Python is a simple yet powerful object-oriented language. Its simplicity makes it easy to learn, but its power means that large and complex applications can also be created easily. Its interpreted nature means that Python programmers are very productive because there is no edit/compile/link/run development cycle.

Python is probably installed automatically by your GNU/Linux distribution (it is on Debian). If not, it is best to use your distribution's standard tools for package installation. On Debian for example:

.. code-block:: bash

    $ sudo apt-get install python python-dev build-essentials python-setuptools


Numeric Python
--------------

*Web-site:*
    http://www.scipy.org/numpy
*Version required:*
    >= 1.0

Numeric Python is a module for fast numeric computations in Python.

Example installation:

.. code-block:: bash

    $ sudo apt-get install python-numpy


Matplotlib
----------

*Web-site:*
    http://matplotlib.sourceforge.net
*Version required:*
    >0.9

Matplotlib is a Module that provides plotting capabilities to Python.

.. code-block:: bash

    $ sudo apt-get install python-matplotlib python-matplotlib-data python-matplotlib-doc


PyQt
----

*Web-site:*
    http://www.riverbankcomputing.co.uk/pyqt
*Version required:*
    >4.0

PyQt is a set of Python bindings for the Qt toolkit. PyQt combines all the advantages of Qt and Python. A programmer has all the power of Qt, but is able to exploit it with the simplicity of Python.

PyQt depends on the Qt libraries to run. This dependency will be taken care by the package installation tools of most distributions, which will automatically install the required version of Qt.

Example installation:

.. code-block:: bash

    $ sudo apt-get install python-qt4

PyQwt
-----

*Web-site:*
    http://pyqwt.sourceforge.net/
*Version required:*
    >5.0

PyQwt is a Python binding for the Qwt5 technical widget library. It is necessary for some os Epigrass' visualizations capabilities.

Example installation:

.. code-block:: bash

    $ sudo apt-get install python-qwt5-qt4

MySQL
-----

*Web-site:*
    http://www.mysql.com
*Version required:*
    >5.0

MySQL is a fast, multi-threaded, multi-user SQL database server. If you have a MySQL server available in your LAN, you may skip this step after making sure you have permission to access and use it to store your data.

Example installation:

.. code-block:: bash

    $ sudo apt-get install mysql-server mysql-client python-mysqldb

Redis
-----

*web-site:*
    http://redis.io
*Version required:*
    >=2.8

Redis is a persistent Key-value database.

Example installation:

.. code-block:: bash

    $ sudo apt-get install redis-server

Other Requirements
------------------

Some other requirements can be installed directly from the Python Package index using the *pip* tool:

.. code-block:: bash

    $ sudo pip install networkx redis sqlsoup requests sphinx


Post-install configuration
""""""""""""""""""""""""""

After installing MySQL, you will need to create a new database in the server, called *epigrass* and a user with all priviledges to access and modify it. This is the user Epigrass will use to interact with MySQL.




\section{Installing Epigrass}
If you got through all the steps above, it will be an easy task to install Epigrass. There is a *.deb* package for installing Epirass on Debian and Ubuntu. However, since it is not maitained by the developers of Epigrass, It may very well be outdated.  So please download Epigrass's source tarball (something named :file:`Epigrass_someversion.tar.gz`) from Sourceforge and, after unpacking it to some temporary directory, install it by typing:

.. code-block:: bash

    $ sudo python setup.py install


If the installation proceeds without errors, you will have three new executables available on your system:

*epigrass*
    This starts Epigrass graphical user interface (GUI).
*epirunner*
    This is a command line version of Epigrass. With it you can run models without invoking the GUI. It's great for batch simulations and for remote use. for a quick help, try "epirunner -h".
*epgeditor*
    A graphical editor of .epg models. A easy way to edit already existing models. Contains detailed explanations of every section of the EPG file. :math:`x_3+y`
