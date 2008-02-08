"""
This module is a collection of fucntions to interface with "R":http://cran.r-project.org 

You need to have R and the following libraries installed for it to work:

*RMySQL

*DBI

*lattice
"""
from rpy import *

def qnplot(table):
    """
    This function query simulation results stored in a MySQL table
    and generates some plots.
    """
    s = """library(DBI)
    library(RMySQL)
    library(lattice)
    drv <- dbDriver("MySQL")
    con <- dbConnect(drv, username='root',password='mysql', host='localhost',dbname='epigrass')
    results<- dbReadTable(con,'%s')
    names(results)
    par(mfrow=c(2,2))
    plot(results$I[results$geocode==230440005],type='l',main='Fortaleza')
    plot(results$I[results$geocode==355030800],type='l',main='São Paulo')
    plot(results$I[results$geocode==520880605],type='l',main='goianira')
    plot(results$I[results$geocode==510760205],type='l',main='Rondonopolis')
    x11()
    xyplot(I~as.numeric(time),type="l",groups=results$geocode,data=results)
    """ % table
    r(s)
