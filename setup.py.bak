# -*- coding:utf8 -*-
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup
from glob import glob
#from distutils.core import setup

demos = glob('demos/*')
try:
    demos.remove('demos/CVS')
except: pass

setup(name='epigrass',
    version='2.0b3',
    author = 'Flavio Codeco Coelho, Claudia Torres Codeco',
    author_email = 'fccoelho@gmail.com',
    maintainer = 'Flavio Codeco Coelho',
    maintainer_email = 'fccoelho@gmail.com',
    url = 'http://epigrass.sourceforge.net',
    description = 'Epidemiological Geo-Referenced Analysis and Simulation System',
    long_description = 'EpiGrass is a simulator of epidemics over networks.  Its is a scientific tool created for simulations and scenario analysis in Network epidemiology.',
    download_url = 'http://sourceforge.net/project/showfiles.php?group_id=128000',
    license = 'GPL',
    packages = ['Epigrass'],
    entry_points = {
        'console_scripts': [
            'epirunner = Epigrass.manager:main',
        ],
        'gui_scripts': [
            'epigrass = Epigrass.epigrass:main',
            'epgeditor= Epigrass.epgeditor:main'
        ]
    }, 

    include_package_data = True,
    package_data = {'':['INSTALL','README','COPYING','epigrass.desktop']},
    data_files = [('/usr/share/pixmaps',['egicon.png']),('/usr/share/doc/epigrass/demos',demos),('/usr/share/doc/epigrass/',['docs/build/latex/Epigrass.pdf']),('/usr/share/applications',['epigrass.desktop'])]
    )
