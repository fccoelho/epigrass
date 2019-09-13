"""
This module contains functions to read and write from ascii files, as well as to/from MySQL databases.
"""
from __future__ import absolute_import
from __future__ import print_function
from numpy import *
from string import *
import codecs
#from sqlobject import *

from difflib import *
import sys
from six.moves import range
from six.moves import zip

def load(fname, sep=None):
    """
    Load ASCII data from fname into an array and return the array.

    The data must be regular, same number of values in every row

    fname must be a filename.
    
    optional argument sep must be set if the separators are not some kind of white space.

    well suited for GRASS ascii site data.

    Example usage::

    x,y = load('test.dat')  # data in two columns

    X = load('test.dat')    # a matrix of data

    x = load('test.dat')    # a single column of data
    
    X = load('test.dat, sep = ',') # file is csv

    """
    with codecs.open(fname,'r') as f:
        linelist = f.readlines()
    
    
    X = []
    numCols = None
    for line in linelist:
        line = line.strip()
        if not len(line): continue
        row = [float(val) for val in line.split(str(sep))]
        thisLen = len(row)
        if numCols is not None and thisLen != numCols:
            raise ValueError('All rows must have the same number of columns')
        X.append(row)

    X = array(X)
    r,c = X.shape
    if r==1 or c==1:
        X.shape = max([r,c]),
    return X
    
def loadData(fname,sep = ',', encoding='utf-8'):
    """
    Loads from ascii files with separated values
    and returns a list of lists.
    """
    f = codecs.open(fname,'r',encoding='utf8')
    linelist = f.readlines()
    f.close()
    
    sitelist = []
    #numCols = None
    for line in linelist:
        line = line.strip()
        #if not len(line): continue
        row = [elmt.strip() for elmt in line.split(str(sep))]
        #thisLen = len(row)
        #if numCols is not None and thisLen != numCols:
        #    raise ValueError('All rows must have the same number of columns')
        sitelist.append(row)
        
    return sitelist
    
def queryDb(usr,passw,db,table, host='localhost',port=3306,sql=''):
    """
    Fetch the contents of a table on a MySQL database
    sql,usr,passw,db,table and host must be strings.
    returns a tuple of tuples and a list of dictionaries.
    """
    import MySQLdb
    con = MySQLdb.connect(host=host, port=port, user=usr,passwd=passw, db=db)
    Cursor = con.cursor()
    #get column names
    Cursor.execute('show columns from '+table)
    cout = Cursor.fetchall()
    cnames=[]
    for i in cout:
        cnames.append(i[0])
        
    if sql == '':
        sql = 'SELECT * FROM ' + table
    Cursor.execute(sql)
    results = Cursor.fetchall()
    con.close()
    res=[]
    for i in results: #creates a list of dictionaries
        res.append(dict([x for x in zip(cnames,i)]))
        
    return res
    
    
def loadEdgeData(fname):
    """
    """
    fname = 'antt2002TODOS.csv'
    dados = loadData(fname ,',')
    dicCity = queryDb('root','mysql','epigrass','localidades')
    dados[0].append('codigo1')
    dados[0].append('codigo2')
    for i in range(1,len(dados)):
        cidade1 = dados[i][1].lower() #word
        UF1 = dados[i][2]
        cidade2 = dados[i][3].lower() #word2
        UF2 = dados[i][4]
        
        ln1 = [x['NM_NOME'].lower() for x in dicCity if  x['UF'] == UF1]
        ld1 = [x for x in dicCity if  x['UF'] == UF1]
        mat = get_close_matches(cidade1,ln1,5)
        if not mat:
            dados[i].append('NA')
        else:
            geoc1 = [x['GEOCODIGO'] for x in ld1 if x['NM_NOME'].lower() == mat[0]]
            #print i,mat[0] 
            try:
                dados[i].append(geoc1[0])
            except IndexError:
                print('No match for city name ', cidade1)
                sys.exit()
        #print cidade1,UF1, mat
        
        ln2 = [x['NM_NOME'].lower() for x in dicCity if  x['UF'] == UF2]
        ld2 = [x for x in dicCity if  x['UF'] == UF2]
        mat2 = get_close_matches(cidade2,ln2,5)
        if not mat2:
            dados[i].append('NA')
        else:
            geoc2 = [x['GEOCODIGO'] for x in ld2 if x['NM_NOME'].lower() == mat2[0]]
            try:
                dados[i].append(geoc2[0])
            except IndexError:
                print('No match for city name ', cidade2)
                sys.exit()
        #print cidade2,UF2, mat2
        
    fout = open('edgesout.csv','w')
    for i in dados:
        for j in i:
            fout.write(j+',')
        fout.write('\n')
    fout.close()
    return dados
    
def getSiteFromGeo(fin=None,fout=None):
    """
    Search the locality and census databases tables for codes in a file and creates a
    sites file.
    """
    if not fin:
        fname = 'scodes.csv'
    else:
        fname = fin
    f = open (fname, 'r')
    codes = f.readlines()
    dicCity = queryDb('root','mysql','epigrass','localidades')
    dicTodos = queryDb('root','mysql','epigrass','universo')
    sitios = ['latitude,longitude,localidade,populacao urb.,geocodigo\n']#header
    x=0
    for i in codes:
        for j in dicCity:
            #x+=1;print x
            #print len(strip(i)),'g2: ',len(j['GEOCODIGO']),type(i), type(j['GEOCODIGO'])
            if j['GEOCODIGO'] == strip(i):
                line = j['MD_LATITUD']+','+j['MD_LONGITU']+','+j['NM_NOME']
        for k in dicTodos:
            if k['ID_'] == i[:6]:
                line = line+','+str(k['V04'])+','+strip(i)+'\n'
        sitios.append(line)
    f.close()
    #print sitios[0]
    if not fout:
        fout='sitios.csv'
    outf = open(fout,'w')
    outf.writelines(sitios)
    outf.close()
    
    
def sitesToDb(fname,table,db='epigrass',usr='root',passw='mysql', host='localhost',port=3306):
    """
    Creates a site table on a mysql db from a sites file (fname).
    """
    import MySQLdb
    try:
        #now = time.asctime().replace(' ','_').replace(':','')
        #table = #table+'_'+now
        con = MySQLdb.connect(host=host, port=port, user=usr,passwd=passw, db=db)
        Cursor = con.cursor()
        sql = """CREATE TABLE %s(
        `latitude` VARCHAR( 12 ) DEFAULT '0' NOT NULL ,
        `longitude` VARCHAR( 12 ) DEFAULT '' NOT NULL,
        `locality` VARCHAR(64),
        `population` INT(11),
        `geocodigo` INT(9)
        );
        """ % table
        Cursor.execute(sql)
        
        f = open(fname,'r')
        listsites = f.readlines()
        f.close()
        
        sql2 = 'INSERT INTO %s' % table + ' VALUES(%s,%s,%s,%s,%s)'
        for site in listsites:
            values = tuple([strip(i) for i in site.split(',')])
            Cursor.execute(sql2,values)
    finally:
        con.close()    
    
    
