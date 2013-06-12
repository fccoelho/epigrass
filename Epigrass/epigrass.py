#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, os
import logging.handlers

LOG_FILENAME = os.path.join(os.environ['HOME'], 'epigrass_errors.out')
epigrassLogger = logging.getLogger('epigrassLogger')
epigrassLogger.setLevel(logging.ERROR)
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=20000, backupCount=1)
epigrassLogger.addHandler(handler)

try:
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import *
except ImportError:
    epigrassLogger.error("Please install PyQT 4")
    print "Please install PyQT 4"

from manager import *
import threading, subprocess, glob
from Ui_cpanel4new import Ui_MainWindow
from Ui_about4 import Ui_aboutDialog as aboutDialog
import sys, ConfigParser, string, copy, commands, getpass
import epiplay as epi
import spread, dgraph


class MainWindow_Impl(QtGui.QMainWindow, Ui_MainWindow):
    sequenceNumber = 1
    windowList = []

    def __init__(self):
        QtGui.QMainWindow.__init__(self, None)
        self.app = app
        self.QtCore = QtCore
        self.setupUi(self)
        #determining the user's home directory
        home = os.curdir                        # Default
        if 'HOME' in os.environ:
            home = os.environ['HOME']
        elif os.name == 'posix':
            home = os.path.expanduser("~/")
        elif os.name == 'nt':
            if 'HOMEPATH' in os.environ:
                if 'HOMEDRIVE' in os.environ:
                    home = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
                else:
                    home = os.environ['HOMEPATH']
        self.home = home
        self.epigrassrc = os.path.join(home, ".epigrassrc")
        # set Translation
        self.curdir = os.getcwd()
        self.rootdir = os.getcwd()
        if os.access(self.epigrassrc, os.F_OK):
            try:
                self.conf = self.loadRcFile(self.epigrassrc)
                lang = self.conf['settings.language']
            except:
                lang = ''
                #print lang
        else:
            lang = ''
        tr = QtCore.QTranslator(app)
        loadLang(app, tr, lang)

        # Overload connections
        self.connect(self.editButton, QtCore.SIGNAL("released()"), self.editScript)
        self.connect(self.chooseButton, QtCore.SIGNAL("released()"), self.chooseScript)
        self.connect(self.buttonExit, QtCore.SIGNAL("released()"), self.onExit)
        self.connect(self.buttonRun, QtCore.SIGNAL("released()"), self.onRun)#Thread)
        self.connect(self.buttonHelp, QtCore.SIGNAL("released()"), self.onHelp)
        self.connect(self.dbBackup, QtCore.SIGNAL("released()"), self.onDbBackup)
        self.connect(self.dbInfo, QtCore.SIGNAL("released()"), self.onDbInfo)
        #        self.connect(self.repOpen,QtCore.SIGNAL("released()"),self.onRepOpen)
        self.connect(self.playButton, QtCore.SIGNAL("released()"), self.onPlayButton)
        #        self.connect(self.playButton_2D,QtCore.SIGNAL("released()"),self.onPlayButton_2D)
        self.connect(self.dbscanButton, QtCore.SIGNAL("released()"), self.onVisual)
        self.connect(self.consensusButton, QtCore.SIGNAL("released()"), self.onConsensus)
        self.connect(self.tableList, QtCore.SIGNAL("activated(int)"), self.getVariables)
        self.connect(self.dbType, QtCore.SIGNAL("activated(int)"), self.setBackend)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.upGUITimer = QtCore.QTimer()
        self.connect(self.upGUITimer, QtCore.SIGNAL("timeout()"), app.processEvents)
        self.upGUITimer.start(100)

        usern = getpass.getuser() #Get the user name
        #check if rc file exists if not, creates one
        if not os.access(self.epigrassrc, os.F_OK):
            self.initRc()

        else:#read existing configuration file
            self.conf = self.loadRcFile(self.epigrassrc)
            self.fillGui(self.conf)
        self.sim = None

    def openGraphDisplay(self, shp='', namefield='', geocfield='', nlist=[], elist=[]):
        """
        Starts the Qt map display
        shp: shapefile fname
        """
        self.graphDisplay = dgraph.MapWindow()
        self.windowList.append(self.graphDisplay)
        #self.graphDisplay.move(self.x()+40, self.y()+40)
        if shp:
            self.graphDisplay.drawMap(shp, namefield, geocfield)
        else:
            self.graphDisplay.drawGraph(nlist, elist)
        self.graphDisplay.show()

    def initRc(self):
        """
        Initializes the epigrassrc file.
        """
        usern = getpass.getuser() #Get the user name
        f = open(self.epigrassrc, 'w')

        rcskel = ['#EpiGrass Configuration File',
                  '[model]',
                  'script=script.epg',
                  '[database]',
                  'backend=sqlite',
                  'host=localhost',
                  'port=3306',
                  'user=epigrass',
                  '[settings]',
                  'name=John Doe',
                  'editor=kate',
                  'pdfviewer=kghostview',
                  'language=en'
        ]
        for i in rcskel:
            f.write(i)
            f.write('\n')
        f.close()
        #fills the gui with default values
        self.conf = self.loadRcFile(self.epigrassrc)
        self.fillGui(self.conf)
        os.chdir(self.curdir)

    def updateRc(self):
        """
        Updates the epigrassrc file with the contents of the configuration
        dictionary.
        """
        usern = getpass.getuser() #Get the user name

        if os.access(self.epigrassrc, os.F_OK):
            os.remove(self.epigrassrc)
        f = open(self.epigrassrc, 'w')

        rcskel = ['#EpiGrass Configuration File',
                  '[model]',
                  'script=%s' % self.conf['model.script'],
                  '[database]',
                  'backend=%s' % self.conf['database.backend'],
                  'host=%s' % self.conf['database.host'],
                  'port=%s' % self.conf['database.port'],
                  'user=%s' % self.conf['database.user'],
                  '[settings]',
                  'name=%s' % self.conf['settings.name'],
                  'editor=%s' % self.conf['settings.editor'],
                  'pdfviewer=%s' % self.conf['settings.pdfviewer'],
                  'language=%s' % self.conf['settings.language']
        ]
        for i in rcskel:
            f.write(i)
            f.write('\n')
        f.close()


    def loadRcFile(self, fname, config={}):
        """
        Loads epigrassrc.
        Returns a dictionary with keys of the form
        <section>.<option> and the corresponding values.
        """
        config = config.copy()
        cp = ConfigParser.SafeConfigParser()
        cp.read(fname)
        for sec in cp.sections():
            name = string.lower(sec)
            for opt in cp.options(sec):
                config[name + "." + string.lower(opt)] = string.strip(cp.get(sec, opt))
        os.chdir(self.curdir)
        return config

    def fillGui(self, conf):
        """
        Fill the gui fields from configuration dictionary conf.
        """
        if self.conf['settings.language'] == 'pt_BR':
            self.langCombo.setCurrentIndex(1)
        elif self.conf['settings.language'] == 'fr':
            self.langCombo.setCurrentIndex(2)
        elif self.conf['settings.language'] == 'ru':
            self.langCombo.setCurrentIndex(3)
        elif self.conf['settings.language'] == 'es':
            self.langCombo.setCurrentIndex(4)
        else:
            self.langCombo.setCurrentIndex(0)
        try:
            self.scriptNameEdit.setText(conf['model.script'])
            self.hostnEdit.setText(conf['database.host'])
            self.portEdit.setText(conf['database.port'])
            self.uidEdit.setText(conf['database.user'])
            self.unameEdit.setText(conf['settings.name'])
            self.editorEdit.setText(conf['settings.editor'])
            self.pdfEdit.setText(conf['settings.pdfviewer'])
        except KeyError, v:
            V = v.__str__().split('.')
            QMessageBox.information(None,
                                    self.trUtf8("Syntax Error"),
                                    self.trUtf8("""Please check file .epigrassrc for missing %s keyword
                from section %s """ % (V[1], V[0])))
        ##            usern = pwd.getpwuid(os.getuid())[0] #Get the user name
        ##            os.system('rm /home/'+usern+'.epigrassrc')
        ##            self.initRc()

    def checkConf(self):
        """
        Check if the configuration dictionary is complete
        """
        if not self.conf:
            self.initRc()
        for i in self.conf.items():
            if not i[1]:
                QMessageBox.information(None,
                                        self.trUtf8("Incomplete Configuration"),
                                        self.trUtf8("""Please enter a value for %s.""" % i[0]),
                                        self.trUtf8("&OK"))
                return 0
        return 1


    def editScript(self):
        """
        Opens the model script with the user's preferred editor.
        """
        if self.editorEdit.text() and self.scriptNameEdit.text():
            ed = str(self.editorEdit.text())
            scr = str(self.scriptNameEdit.text())
            os.system('%s %s' % (ed, scr))
        else:
            QMessageBox.warning(None,
                                self.trUtf8("Editor or Script not selected"),
                                self.trUtf8("""Please make sure you have selected both
an editor and your model's script."""),
                                self.trUtf8("&OK"))


    def chooseScript(self):
        """
        starts the file selction dialog for the script.
        """
        scrname = QFileDialog.getOpenFileName( \
            None,
            self.trUtf8("Select your Model's Script"),
            QtCore.QString(),
            self.trUtf8("*.epg"),
            None)


        #        scrname = QFileDialog.getOpenFileName(\
        #                    QtCore.QString.null,
        #                    self.trUtf8("*.epg"),
        #                    None, None,
        #                    self.trUtf8("Select your Model's Script"),
        #                    None, 1)
        self.scriptNameEdit.setText(scrname)
        self.conf['model.script'] = scrname

    def readGui(self):
        """
        Gets the info from the GUI into the configuration dictionary.
        """
        self.conf['model.script'] = str(self.scriptNameEdit.text())
        self.conf['database.host'] = str(self.hostnEdit.text())
        self.conf['database.port'] = int(str(self.portEdit.text()))
        self.conf['database.user'] = str(self.uidEdit.text())
        self.conf['database.backend'] = str(self.dbType.currentText()).lower()
        self.conf['settings.name'] = unicode(str(self.unameEdit.text()))
        self.conf['settings.editor'] = str(self.editorEdit.text())
        self.conf['settings.pdfviewer'] = str(self.pdfEdit.text())

        os.chdir(os.path.split(self.conf['model.script'])[0])
        #print os.getcwd()

        if int(self.langCombo.currentIndex()) == 1:
            self.conf['settings.language'] = 'pt_BR'
        elif int(self.langCombo.currentIndex()) == 2:
            self.conf['settings.language'] = 'fr'
        elif int(self.langCombo.currentIndex()) == 3:
            self.conf['settings.language'] = 'ru'
        elif int(self.langCombo.currentIndex()) == 4:
            self.conf['settings.language'] = 'es'
        else:
            self.conf['settings.language'] = 'en'


    def onRun(self):
        """
        starts the simulation when the run button is pressed
        """
        self.stepLCD.display(0)
        self.tabWidget.setCurrentIndex(2)
        self.readGui()
        self.updateRc()
        if self.checkConf():
            if not self.dbType.currentIndex():
                if not self.pwEdit.text():
                    QMessageBox.warning(None,
                                        self.trUtf8("Missing Database Password"),
                                        self.trUtf8("""Please enter password for MySQL database."""))
                    return
            self.buttonRun.setEnabled(0)
            self.sim = S = simulate(fname=self.conf['model.script'], host=self.conf['database.host'],
                                    port=int(self.conf['database.port']),
                                    db='epigrass', user=self.conf['database.user'], password=str(self.pwEdit.text()),
                                    backend=str(self.dbType.currentText()).lower())
            S.gui = self
            #            if S.shapefile:
            #                self.openGraphDisplay(S.shapefile[0], S.shapefile[1],S.shapefile[2] )

            self.RT = RunThread(S)
            #            QtCore.QObject.connect(self.RT,QtCore.SIGNAL("drawStep"), self.graphDisplay.drawStep)
            if not S.replicas:
                self.RT.start()

                self.buttonRun.setEnabled(1)
            else: #Repeated runs 
                self.repRuns(S)
                self.buttonRun.setEnabled(1)


            # In case of a batch
            if S.Batch:
                self.textEdit1.insertPlainText(self.trUtf8('Simulation Started.'))

                # run the batch list
                for i in S.Batch:
                    #Makes sure it comes back to original directory before opening models in the batch list
                    os.chdir(self.sim.dir)
                    # Generates the simulation object        
                    self.sim = T = simulate(fname=i, host=self.conf['database.host'],
                                            port=int(self.conf['database.port']),
                                            db='epigrass', user=self.conf['database.user'],
                                            password=str(self.pwEdit.text()),
                                            backend=str(self.dbType.currentText()).lower())
                    T.gui = self
                    print 'starting model %s' % i
                    T.start()  # Start the simulation 

            self.textEdit1.insertPlainText('Done!')
            self.buttonRun.setEnabled(1)
            #print 'Agora...'
            spread.Spread(self.sim.g, self.sim.outdir, self.sim.encoding)

            #spdisp.display()
        else:
            self.buttonRun.setEnabled(1)
            return


    def repRuns(self, S):
        """
        Do repeated runs
        """
        nseeds = S.seed[0][2] #number o individual to be used as seeds
        randseed = S.randomize_seeds
        print "replicas type", randseed
        if randseed:
            seeds = S.randomizeSeed(randseed)
        reps = S.replicas
        for i in xrange(reps):
            print "Starting replica number %s" % i
            self.textEdit1.insertPlainText("Starting replica number %s" % i)
            self.sim = S = simulate(fname=self.conf['model.script'], host=self.conf['database.host'],
                                    port=int(self.conf['database.port']),
                                    db='epigrass', user=self.conf['database.user'], password=str(self.pwEdit.text()),
                                    backend=str(str(self.dbType.currentText()).lower()))
            S.gui = self
            if randseed:
                S.setSeed(seeds[i], nseeds)
            S.round = i
            S.shpout = False
            S.start()
            del S, self.sim

        #            if S.Rep: #Generate report if necessary
        #                rep = Rp.report(S)
        #                self.textEdit1.insertPlainText('Report generation started.')
        #                rep.Assemble(S.Rep)
        #            del S

    def onDbBackup(self):
        """
        Dumps the epigrass databse to an sql file.
        """
        if self.conf['database.host'] != 'localhost':
            QMessageBox.warning(None,
                                self.trUtf8("Non-local Database Server"),
                                self.trUtf8("""Currently, the database backup function only
                works on local database servers."""),
                                self.trUtf8("&OK"))

        os.system('mysqldump -u %s -p%s --opt epigrass > epigrass.sql' % (str(self.uidEdit.text()), self.pwEdit.text()))

        QMessageBox.information(None,
                                self.trUtf8("Restore Instructions:"),
                                self.trUtf8("""The epigrass database has been Backed up
to a file named "epigrass.sql".
This file is in you current working directory.
To restore the database type:
epigrass.sql > mysql"""),
                                self.trUtf8("&OK"))

    def onDbInfo(self):
        pass

    def onHelp(self):
        """
        Opens the userguide
        """
        aboutD = QtGui.QDialog()
        ab = aboutDialog()
        ab.setupUi(aboutD)
        aboutD.show()
        aboutD.exec_()

    #        if os.path.exists('/usr/share/epigrass/docs/Epigrass.pdf'):
    #            try:
    #                os.system('%s /usr/share/epigrass/docs/Epigrass.pdf'%str(self.pdfEdit.text()))
    #            except:
    #                QMessageBox.warning(None,
    #                    self.trUtf8("Help not available"),
    #                    self.trUtf8("""Could not open user guide.
    #    Please make sure your chosen PDF viewer is installed."""),
    #                    self.trUtf8("&OK"))

    def onRepOpen(self):
        """
        Opens the report PDF
        """

        out = commands.getstatusoutput('%s %s' % (self.conf['settings.pdfviewer'], self.sim.repname))
        if out[0] != 0:
            QMessageBox.warning(None,
                                self.trUtf8("No Report"),
                                self.trUtf8("""Could not open the report.
Make sure you have generated it."""),
                                self.trUtf8("&OK"))


    def find_data_dirs(self):
        print "scanning"
        basedir = self.rootdir
        os.chdir(basedir)
        datadirs = [] #list of  outdata directories
        while datadirs == []:
            basedir = str(QFileDialog.getExistingDirectory( \
                None,
                self.trUtf8("Select a Directory"),
                QtCore.QString(),
                QFileDialog.Options(QFileDialog.ShowDirsOnly)))
            os.chdir(basedir)
            datadirs = [d for d in glob.glob("outdata-*") if os.path.isdir(d)] #list of  outdata directories

        return basedir, datadirs

    def onVisual(self):
        """
        Scan the epigrass database an shows available simulations.
        """
        basedir, datadirs = self.find_data_dirs()
        if self.dbType.currentIndex() == 0:
            if not self.pwEdit.text():
                QMessageBox.warning(None,
                                    self.trUtf8("Missing Database Password"),
                                    self.trUtf8(
                                        """Please enter the password for the MySQL database in the first tab."""))
                return
        # for SQLite databases check for the existence os the database file.
        elif self.dbType.currentIndex() == 1:
            print "sqlite"
            if len(datadirs) > 1:
                datadir = str(QtGui.QInputDialog.getItem( \
                    None,
                    self.trUtf8("Please Select Database to Open"),
                    self.trUtf8("Database"),
                    datadirs,
                    0, False)[0])
            elif len(datadirs) == 0:
                QtGui.QMessageBox.critical(None,
                                           self.trUtf8("Invalid Folder"),
                                           self.trUtf8(
                                               """This directory does not contain a model outdata subdirectory. """),
                                           QtGui.QMessageBox.StandardButtons( \
                                               QtGui.QMessageBox.Abort))

            else:
                datadir = datadirs[0]
            print basedir
            print datadir
            fulldatadir = os.path.join(basedir, datadir)
            os.chdir(fulldatadir)
            print os.getcwd()
            if not os.path.exists('Epigrass.sqlite'):
                QtGui.QMessageBox.warning(None,
                                          self.trUtf8("No Database found"),
                                          self.trUtf8("""Please try again"""),
                                          QtGui.QMessageBox.StandardButtons( \
                                              QtGui.QMessageBox.Ok))
                os.chdir(basedir)
                print os.getcwd()

        self.Display = epi.viewer(host=str(self.hostnEdit.text()), port=int(str(self.portEdit.text())),
                                  db='epigrass', user=str(self.uidEdit.text()), pw=str(self.pwEdit.text()),
                                  backend=self.conf['database.backend'], gui=self)
        os.chdir(fulldatadir)

        for s in self.Display.tables:
            if s.endswith('_meta'):
                self.tableList.insertItem(0, s[:-5])
            #check for available maps
        maplist = [i for i in os.listdir(os.getcwd()) if i.endswith('.shp')]
        for m in maplist:
            self.mapList.insertItem(0, m)

    def getVariables(self):
        """
        Fill the variables list whenever a table is selected in the table list
        """
        self.variableList.clear()
        table = str(self.tableList.currentText())
        self.vars = self.Display.getFields(table)
        for s in self.vars:
            if s not in ['id', 'name', 'geocode', 'lat', 'longit', 'time']:
                self.variableList.insertItem(0, s)
                #TODO: read meta-info from table and show in the tooltip
            #        self.tableList.setToolTip('')

    def onPlayButton(self):
        """
        Calls the epiplay module to replay the epidemic from a database table.
        """

        #get variable to animate and its position in the database
        var = str(self.variableList.currentText())
        pos = self.vars.index(var)
        r = self.rateSpinBox.value()
        table = str(self.tableList.currentText())
        if self.Display.shapefile:
            mapa = self.Display.shapefile[0]
        else:
            mapa = None
        modname = table.split('_')[0] #self.sim.modelName.split('/')[-1]
        #change to the outdata directory
        if not os.path.split(os.getcwd())[1].startswith("outdata"):
            os.chdir("outdata-" + modname)
        nodes, am = self.Display.readNodes(modname, table)
        if not nodes:
            QMessageBox.warning(None,
                                self.trUtf8("Empty Table"),
                                self.trUtf8("""You have selected an empty table.
Please select another table from the menu."""))
            return

        numbnodes = len(nodes)
        data = self.Display.readData(table)
        edata = self.Display.readEdges(table)
        #        os.chdir(self.rootdir)
        numbsteps = len(data) / numbnodes
        self.Display.viewGraph(nodes, am, var, mapa)
        self.Display.anim(data, edata, numbsteps, pos, r)
        #Future(self.Display.keyin,data,edata,numbsteps,pos,r)
        #self.Display.keyin(data,edata,numbsteps,pos,r)


    def onConsensus(self):
        """
        Build the consensus tree
        """

        modelpath = os.path.split(self.conf['model.script'])[0]
        print type(modelpath)

        path = QFileDialog.getExistingDirectory( \
            self.trUtf8(modelpath),
            None, None,
            self.trUtf8("Select Directory with Tree Files (epipath*.csv)"),
            1, 1)
        cutoff = QInputDialog.getDouble( \
            self.trUtf8("Branch Support"),
            self.trUtf8("Enter minimum branch support level to display:"),
            50.0, 0.0, 100.0, 1)
        cons = spread.Consensus(str(path), cutoff)


    def setBackend(self):
        """
        activate/deactivate db spec groupbox
        """
        self.backend = self.conf['database.backend'] = str(self.dbType.currentText()).lower()
        #print self.backend
        if self.dbType.currentIndex():
            self.dbSpecGroupBox.setEnabled(0)
            self.dbBackup.setEnabled(0)
        else:
            self.dbSpecGroupBox.setEnabled(1)
            self.dbBackup.setEnabled(1)

    def onExit(self):
        """
        Close the gui
        """
        self.close()


class Future:
    """
    By David Perry - http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/84317
    To run a function in a separate thread, simply put it in a Future:

    >>> A=Future(longRunningFunction, arg1, arg2 ...)

    It will continue on its merry way until you need the result of your function. 
    You can read the result by calling the Future like a function, for example:

    >>> print A()

    If the Future has completed executing, the call returns immediately. 
    If it is still running, then the call blocks until the function completes. 
    The result of the function is stored in the Future, so subsequent calls to 
    it return immediately.

    A few caveats:
    Since one wouldn't expect to be able to change the result of a function, 
    Futures are not meant to be mutable. This is enforced by requiring the 
    Future to be "called", rather than directly reading __result. If desired, 
    stronger enforcement of this rule can be achieved by playing 
    with __getattr__ and __setattr__.

    The Future only runs the function once, no matter how many times you 
    read it. You will have to re-create the Future if you want to re-run your 
    function; for example, if the function is sensitive to the time of day.

    For more information on Futures, and other useful parallel programming 
    constructs, read Gregory V. Wilson's _Practical Parallel Programming_.
    """

    def __init__(self, func, *param):
        # Constructor
        self.__done = 0
        self.__result = None
        self.__status = 'working'

        self.__C = Condition()   # Notify on this Condition when result is ready

        # Run the actual function in a separate thread
        self.__T = Thread(target=self.Wrapper, args=(func, param))
        self.__T.setName("FutureThread")
        self.__T.start()

    def __repr__(self):
        return '<Future at ' + hex(id(self)) + ':' + self.__status + '>'

    def __call__(self):
        self.__C.acquire()
        while self.__done == 0:
            self.__C.wait()
        self.__C.release()
        # We deepcopy __result to prevent accidental tampering with it.
        a = copy.deepcopy(self.__result)
        return a

    def Wrapper(self, func, param):
        # Run the actual function, and let us housekeep around it
        self.__C.acquire()
        try:
            self.__result = func(*param)
        except:
            self.__result = "Exception raised within Future"
        self.__done = 1
        self.__status = `self.__result`
        self.__C.notify()
        self.__C.release()


def loadLang(app, tr, lang):
    """
    loads the language based on the user's choice.
    """
    if lang == 'pt_BR':
        tr.load('manager_pt_BR', '.')
        app.installTranslator(tr)
    elif lang == 'fr':
        tr.load('epigrass_fr', '.')
        app.installTranslator(tr)
    elif lang == 'es':
        tr.load('epigrass_es', '.')
        app.installTranslator(tr)
    elif lang == 'ru':
        tr.load('epigrass_ru_RU', '.')
        app.installTranslator(tr)
    else:
        pass


def main():
    global app
    app = QtGui.QApplication(sys.argv)
    w = MainWindow_Impl()
    w.show()
    sys.exit(app.exec_())


class RunThread(QtCore.QThread):
    """
    Worker Thread to run the simulation in a separate thread in order to allow the updating of the GUI to take place
    """

    def __init__(self, sim, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.mutex = QtCore.QMutex()
        self.condition = QtCore.QWaitCondition()
        self.sim = sim

    def __del__(self):
        self.mutex.lock()
        self.condition.wakeOne()
        self.mutex.unlock()
        self.wait()

    def go(self):
        locker = QtCore.QMutexLocker(self.mutex)
        self.start()

    def run(self):
        self.sim.start()
        self.mutex.lock()
        self.condition.wait(self.mutex)
        self.mutex.unlock()


if __name__ == "__main__":
    main()
    
    
