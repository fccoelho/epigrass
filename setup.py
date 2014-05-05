# -*- coding:utf8 -*-
from setuptools import setup
from glob import glob
from Epigrass.__version__ import version
#from distutils.core import setup
#TODO: remove dependency on setuptools

demos = glob('demos/*')
try:
    demos.remove('demos/CVS')
except:
    pass

setup(name='epigrass',
      version=version,
      author='Flavio Codeco Coelho, Claudia Torres Codeco',
      author_email='fccoelho@gmail.com',
      maintainer='Flavio Codeco Coelho',
      maintainer_email='fccoelho@gmail.com',
      url='http://epigrass.sourceforge.net',
      description='Epidemiological Geo-Referenced Analysis and Simulation System',
      long_description='EpiGrass is a simulator of epidemics over networks.  Its is a scientific tool created for simulations and scenario analysis in Network epidemiology.',
      download_url='http://sourceforge.net/project/showfiles.php?group_id=128000',
      license='GPL',
      packages=['Epigrass'],
      install_requires=["numpy >= 1.2", "networkx >= 1.1", "SQLAlchemy >= 0.7", "sqlsoup", "redis >= 2.4", "requests"],
      entry_points={
          'console_scripts': [
              'epirunner = Epigrass.manager:main',
          ],
          'gui_scripts': [
              'epigrass = Epigrass.epigrass:main',
              'epgeditor= Epigrass.epgeditor:main',
              'neteditor= Epigrass.neteditor:main'
          ]
      },

      include_package_data=True,
      package_data={'': ['INSTALL', 'README', 'COPYING', 'epigrass.desktop', '*.rst', '*.tex', '*.png', '*.jpg']},
      #data_files = [('/usr/share/pixmaps',['egicon.png']),('/usr/share/doc/epigrass/demos',demos),('/usr/share/doc/epigrass/',['docs/build/latex/Epigrass.pdf']),('/usr/share/applications',['epigrass.desktop'])]
)
