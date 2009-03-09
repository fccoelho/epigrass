#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from PyQt4 import QtCore, QtGui
#    from PyQt4.QtGui import *
except ImportError:
    print "Please install PyQT 4"
from Epigrass.Ui_epgeditor import Ui_MainWindow
from Epigrass.Ui_about4 import Ui_aboutDialog as aboutDialog
import ConfigParser
import StringIO
import epigrass_rc

class Editor(QtGui.QMainWindow,Ui_MainWindow):
    def __init__(self, argv):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        self.cp = ConfigParser.SafeConfigParser()
        if len(argv) <2:
            self.fname = ''
        else:
            self.fname = argv[1]
            self.fillTree(self.fname)
        QtCore.QObject.connect(self.exitButton,QtCore.SIGNAL("clicked()"),self.close)
        self.editing = None
        self.helpBrowser.setSource(QtCore.QUrl("qrc:/HelpEpg.html"))
       
        

    def checkScript(self):
        """
        Checks the loaded script for required headers and variables
        """
        self.fixed = sections = {'TRANSPORTATION MODEL':{'stochastic':0, 'speed':0, 'dotransp':1},
        'THE WORLD':{'sites':'', 'shapefile':'', 'encoding':'', 'edges':''},
        'SIMULATION AND OUTPUT':{'steps':50, 'siterep':[], 'report':0, 'replicas':0, 'randseed':0, 'outdir':'', 'mysqlout':0, 'batch':[]},
        'MODEL PARAMETERS':{'w':0, 'r':1, 'p':0, 'e':1, 'delta':0, 'beta':0, 'b':0, 'alpha':1},
        'INITIAL CONDITIONS':{'s':'N', 'i':0, 'e':0},
        'EPIDEMIOLOGICAL MODEL':{'modtype':'SIR'},
        'EPIDEMIC EVENTS':{'vaccinate':[], 'seed':[], 'quarantine':[]}}
        for i in sections.items():
            try:
                assert (self.cp.has_section(i[0]))
                for v in i[1].items():
                    try:
                        self.cp.get(i[0], v[0])
                    except:
                        QtGui.QMessageBox.information(None,
                            self.trUtf8("Required variable missing"),
                            self.trUtf8("""Variable %s was missing. Variable created and value set to default"""%v))
                        self.cp.set(i[0], v[0],str(v[1]))
            except AssertionError:
                    QtGui.QMessageBox.information(None,
                    self.trUtf8("Required section missing"),
                    self.trUtf8("""Section %s was missing. It was added to your file with default values for its variables."""%i[0]))
                    self.cp.add_section(i[0])
                    for j in i[1].items():
                        self.cp.set (i[0],j[0] , str(j[1]))
        

    def fillTree(self, fname):
        """
        Fills the tree from the configuration file's
        contents. 
        Returns a ConfigParser object
        """
        self.treeWidget.clear()
        self.cp.read(fname)
        self.checkScript()
        self.updateViewer()
        for sec in self.cp.sections():
            topitem = QtGui.QTreeWidgetItem(self.treeWidget)
            topitem.setText(0, sec)
            topitem.setText(1, "---")
            topitem.setText(2, "Section Header")
            self.treeWidget.addTopLevelItem(topitem)
            for opt in self.cp.options(sec):
                chitem = QtGui.QTreeWidgetItem(topitem)
                chitem.setText(0, opt)
                pos = self.cp.get(sec,opt).find('#')
                if pos >=0:
                    value = self.cp.get(sec,opt)[:pos]
                    comment = self.cp.get(sec,opt)[pos:]
                else:
                    value = self.cp.get(sec,opt)
                    comment = "variable"
                chitem.setText(1, value)
                chitem.setText(2, comment)

    def updateViewer(self):
        vf = StringIO.StringIO()
        self.cp.write(vf)
        self.epgView.setPlainText(vf.getvalue())
        vf.close()

    @QtCore.pyqtSignature("")
    def on_action_About_activated(self):
        QtGui.QMessageBox.about(None,
            self.trUtf8("About .EPG Editor"),
            self.trUtf8("""This editor is for creating or modifying .epg files."""))

    @QtCore.pyqtSignature("")
    def on_actionAbout_Epigrass_activated(self):
        aboutD = QtGui.QDialog()
        ab = aboutDialog()
        ab.setupUi(aboutD)
        aboutD.show()
        aboutD.exec_()

    @QtCore.pyqtSignature("")
    def on_action_Open_epg_File_activated(self):
#        print "clicked"
        fname = str(QtGui.QFileDialog.getOpenFileName(\
            None,
            self.trUtf8("Open .epg File"),
            QtCore.QString(),
            self.trUtf8("*.epg"),
            None))
        if fname:
            self.fillTree(fname)
        self.fname = fname

    @QtCore.pyqtSignature("")
    def on_action_New_activated(self):
        fname =  QtGui.QInputDialog.getText(\
            None,
            self.trUtf8("File Name"),
            self.trUtf8("Enter a name for you new .epg file:"),
            QtGui.QLineEdit.Normal)
        print fname
        if fname[1]:
            fname = str(fname[0])
            if not fname.endswith('.epg'):
                fname+='.epg'
            self.fillTree(fname)


    @QtCore.pyqtSignature("")
    def on_addVButton_clicked(self):
        """
        Add a new variable to the current section
        """
        item = QtGui.QInputDialog.getItem(\
            None,
            self.trUtf8("Choose Section"),
            self.trUtf8("Select a section to which you want to add a variable:"),
            self.fixed.keys(),
            0, True)
        if item[1]:
            sec = str(item[0])
            resp = QtGui.QInputDialog.getText(\
                None,
                self.trUtf8("Variable Name"),
                self.trUtf8("Enter the name of the variable to be created"),
                QtGui.QLineEdit.Normal)
            if resp[1]:
                nam = str(resp[0])
                self.cp.set(sec, nam, '')
                self.updateViewer()
#                print sec, type(sec)
                secit = self.treeWidget.findItems(sec, QtCore.Qt.MatchExactly, 0)[0]
                child = QtGui.QTreeWidgetItem(secit)
                child.setText(0, nam)
                secit.addChild(child)
                self.treeWidget.setCurrentItem(child)
                self.treeWidget.scrollToItem(child)
                self.on_treeWidget_itemDoubleClicked(child, 1)
#                print sec,  nam

    @QtCore.pyqtSignature("")
    def on_action_Help_activated(self):
        self.tabWidget.setCurrentIndex(2)

    @QtCore.pyqtSignature("")
    def on_action_Exit_activated(self):
        self.close()

    @QtCore.pyqtSignature("")
    def on_action_Save_activated(self):
        if not self.fname:
            self.fname = str(QtGui.QFileDialog.getSaveFileName(\
                None,
                self.trUtf8("Save File as"),
                self.fname,
                self.trUtf8("*.epg"),
                None)
)

        fo = open(self.fname, 'w')
        self.cp.write(fo)
        fo.close()



    @QtCore.pyqtSignature("QTreeWidgetItem *, int")
    def on_treeWidget_itemDoubleClicked(self, it, col):
#        print it, col
        if not it.parent():
            return #cannot edit sections
        else:
            if col == 0 and (str(it.text(0)) in self.fixed[str(it.parent().text(0))]):
                return#cannot edit required variables names
            self.editing=(it, col)
            self.treeWidget.openPersistentEditor(it, col)

    @QtCore.pyqtSignature("")
    def on_treeWidget_itemSelectionChanged(self):
        if self.editing:
            if str(self.editing[0].text(2)).startswith('#'): #Keep comments if they exist.
                self.cp.set(str(self.editing[0].parent().text(0)),str(self.editing[0].text(0)) , str(self.editing[0].text(1))+'\t'+str(self.editing[0].text(2)))
            else:
                self.cp.set(str(self.editing[0].parent().text(0)),str(self.editing[0].text(0)) , str(self.editing[0].text(1)))
            self.treeWidget.closePersistentEditor(*self.editing)
            self.editing = None
            self.on_action_Save_activated()
            self.updateViewer()
def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = Editor(sys.argv)
    Form.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
