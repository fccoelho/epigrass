"""
This script generates a sites file compatible with the shapefile used in the project
"""

from argparse import ArgumentParser
from dbfread import DBF
import pandas as pd

def extract_data(shapefile, **args):
    table = DBF(shapefile.split('.')[0]+'.dbf')
    sites = pd.DataFrame(list(table))
    return sites




if __name__ == "__main__":
    # Options and Argument parsing for running model from the command line, without the GUI.

    #    parser = OptionParser(usage=usage, version="%prog "+__version__.version)
    parser = ArgumentParser(description="generate a csv file containing the model's sites from a shapefile",
                            prog="extract_sites")
    parser.add_argument("-n", "--name", dest="name",
                        help="Define which column to use for name")
    parser.add_argument("-g", "--geocode",
                        dest="geocode", help="Column to use as geocode. Must be unique numeric id")
    parser.add_argument("-p", "--population",
                        dest="population", help="Column to use for population size")
    parser.add_argument("-o", "--outfile",
                        dest="outfile", default="sites.csv", help="name of the sites file (<something>.csv)")

    parser.add_argument("shapefile", metavar='shapefile', nargs=1,
                        help='Shapefile for the model (.shp).')

    args = parser.parse_args()
    extract_data(**args)

