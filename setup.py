# -*- coding:utf8 -*-
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup
from glob import glob
#from distutils.core import setup

demos = glob('demos/*')
demos.remove('demos/CVS')

setup(name='epigrass',
    version='2.0a1',
    author = 'Flavio Codeco Coelho, Claudia Torres Codeco',
    author_email = 'fccoelho@fiocruz.br',
    maintainer = 'Flavio Codeco Coelho',
    maintainer_email = 'fccoelho@fiocruz.br',
    url = 'http://epigrass.sourceforge.net',
    description = 'Epidemiological Geo-Referenced Analysis and Simulation System',
    long_description = 'EpiGrass is a simulator of epidemics over networks.  Its is a scientific tool created for simulations and scenario analysis in Network epidemiology.',
    download_url = 'http://sourceforge.net/project/showfiles.php?group_id=128000',
    license = 'GPL',
    packages = ['Epigrass'],
    #entry_points = {'gui_scripts':['epigrass = epigrass:main',]},
    entry_points = {
        'console_scripts': [
            'epirunner = Epigrass.manager:main',
        ],
        'gui_scripts': [
            'epigrass = Epigrass.epigrass:main',
            'epgeditor= Epigrass.epgeditor:main'
        ]
    }, 

    
    #scripts = ['epigrass.py','epgeditor.py'],
    include_package_data = True,
    package_data = {'':['INSTALL','README','COPYING','epigrass.desktop']},
    data_files = [('/usr/share/pixmaps',['egicon.png']),('/usr/share/doc/epigrass/demos',demos),('/usr/share/doc/epigrass/',['docs/userguide.pdf']),('/usr/share/applications',['epigrass.desktop'])]
    )
