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
    >= 3.6


Python is a simple yet powerful object-oriented language. Its simplicity makes it easy to learn, but its power means that large and complex applications can also be created easily. Its interpreted nature means that Python programmers are very productive because there is no edit/compile/link/run development cycle.

Python is probably installed automatically by your GNU/Linux distribution (it is on Debian). If not, it is best to use your distribution's standard tools for package installation. On Debian for example:

.. code-block:: bash

    $ sudo apt-get install python build-essentials python3-pip


Redis database
--------------

*Web-site:*
    https://redis.io
*Version required:*
    >= 6.0

Redis is an in-memory database that Epigrass uses as a message broker for parallel execution.
Example installation:

.. code-block:: bash

    $ sudo apt-get install redis-server



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

    $ sudo pip install  cython networkx redis sqlsoup requests sphinx


Post-install configuration
""""""""""""""""""""""""""

After installing MySQL, you will need to create a new database in the server, called *epigrass* and a user with all priviledges to access and modify it. This is the user Epigrass will use to interact with MySQL.




Installing Epigrass
===================
If you got through all the steps above, it will be an easy task to install Epigrass.
There is a *.deb* package for installing Epirass on Debian and Ubuntu. However, since it is not maintained by the developers of Epigrass, It may very well be outdated.  So we recommend that you install the latest version from PyPI,  by typing:

.. code-block:: bash

    $ sudo pip3 install -U epigrass


If the installation proceeds without errors, you will have three new executables available on your system:

*epirunner*
    This is a command line version of Epigrass. With it you can run models without invoking the GUI. It's great for batch simulations and for remote use. for a quick help, try "epirunner -h".
