# Module for interacting with the database backend through SQLObject 
# 10/2005 - Flavio Codeco Coelho
from    sqlobject import *
import sys,os

#initialization data -- to be reset by calling module
##backend='mysql'
##user='root'
##pw='mysql'
##host='localhost'
##db='epigrass'

def Connect(backend, user, pw, host, port, db):
    """
    Initializes the connection.
    """

    db_filename = os.path.abspath('Epigrass.sqlite')
    ##if os.path.exists(db_filename):
    ##    os.unlink(db_filename)
    if backend == 'sqlite':
        connection_string = 'sqlite:' + db_filename
    elif backend == 'mysql':
        connection_string = r'%s://%s:%s@%s:%s/%s'%(backend,user,pw,host,port,db)
    elif backend == 'postgresql':
        # TODO: check this connection string
        connection_string = r'%s://%s:%s@%s:%s/%s'%(backend,user,pw,host,port,db)
    else:
        sys.exit('Invalid Database Backend specified: %s'%backend)
    connection = connectionForURI(connection_string)
    sqlhub.processConnection = connection.transaction()
    


class Site(SQLObject):
    class sqlmeta:
        name = 'site'
        lazyUpdate = True
    geocode = IntCol()
    time = IntCol()
    totpop = IntCol()
    name = UnicodeCol() 
    lat = FloatCol()
    longit = FloatCol()
     
    
class Edge(SQLObject):
    #_table = 'site'+'e'
    source_code = IntCol()
    dest_code = IntCol()
    time = IntCol()
    ftheta = FloatCol()
    btheta =FloatCol()
    class sqlmeta:
        name = 'site'+'e'
        lazyUpdate = True
    
if __name__ =='__main__':
    Connect('mysql','root','mysql','localhost', 3306, 'epigrass')
    Site._table='testando'
    Site.createTable()
    Edge.createTable()
    dicin={'geocode':0000000,'time':0,'name':'euheim','totpop':100,'lat':10.1,'longit':20.3}
    
    for i in xrange(1):
        pid = os.fork()
        if pid:
            pass
        else:
            Site(**dicin)
            Site._connection.commit()
            print "commit from process %d"%os.getpid()
            sys.exit()

