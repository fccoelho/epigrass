# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/flavio/Documents/Projetos/Epigrass/Epigrass-devel/cpanel.ui'
#
# Created: Qui Jun 28 18:44:11 2007
#      by: The PyQt User Interface Compiler (pyuic) 3.17
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x20\x00\x00\x00\x20" \
    "\x08\x06\x00\x00\x00\x73\x7a\x7a\xf4\x00\x00\x00" \
    "\xdc\x49\x44\x41\x54\x58\x85\xed\x96\x59\x0e\xc3" \
    "\x20\x0c\x44\x1f\x55\xef\x55\x1f\x9d\x9b\x39\x1f" \
    "\x55\x22\x67\x81\x62\x16\xd1\x56\x19\x29\x5f\x04" \
    "\x66\x0c\xc3\x98\x00\x40\x44\x59\x21\x04\x3c\x68" \
    "\x99\x0b\x3c\xcf\xeb\x45\xbd\xfa\x31\x05\x41\xbc" \
    "\x9c\x79\x01\x82\x78\xab\x70\x09\x4e\xc2\x5b\x79" \
    "\x2f\x3c\x66\x90\xde\x02\x6e\x01\x5f\x25\xe0\x7d" \
    "\xe7\x4b\xd2\xac\x31\xf1\x52\x28\x4e\xc2\xd6\xc4" \
    "\x2b\x16\x90\x49\xc2\xb1\x41\x35\x2b\x09\x4f\x3b" \
    "\x60\x91\x39\x8e\x71\x1e\x38\x92\x5f\x91\xd9\x31" \
    "\x35\x47\x13\x68\x30\xa7\xad\xb6\xf4\x38\x22\x51" \
    "\x15\xb6\xaf\x9a\xdc\x92\x7a\xbd\xd0\x55\xc0\x0c" \
    "\x23\xfe\x46\x12\x66\x8d\xd6\xeb\x4d\xa8\x02\x21" \
    "\xa6\x3c\x20\x86\x6f\x3f\x2e\xc8\x36\xb7\x06\xd3" \
    "\x77\xc0\xac\x53\x6f\xc0\x96\xb9\xd3\x4d\xb8\x43" \
    "\x6d\x25\xff\xb3\x03\xe0\xaf\x66\x48\x78\x79\x7a" \
    "\x41\x2b\x57\xf2\xda\xac\x8b\xbf\x4c\x06\xac\x57" \
    "\x30\xd7\x29\xbb\xe2\xd8\xed\x46\xf4\x8b\x8f\x15" \
    "\x74\xeb\xf7\x09\x2c\x49\xf5\x7d\xcb\x80\x93\xf4" \
    "\xd9\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60" \
    "\x82"

class MainPanel(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("MainPanel")

        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding,0,0,self.sizePolicy().hasHeightForWidth()))
        self.setMinimumSize(QSize(560,480))
        self.setIcon(self.image0)


        LayoutWidget = QWidget(self,"progress_Layout")
        LayoutWidget.setGeometry(QRect(11,415,538,25))
        progress_Layout = QHBoxLayout(LayoutWidget,6,6,"progress_Layout")

        self.textLabel1_6 = QLabel(LayoutWidget,"textLabel1_6")
        self.textLabel1_6.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed,0,0,self.textLabel1_6.sizePolicy().hasHeightForWidth()))
        progress_Layout.addWidget(self.textLabel1_6)

        self.stepLCD = QLCDNumber(LayoutWidget,"stepLCD")
        self.stepLCD.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.stepLCD.sizePolicy().hasHeightForWidth()))
        progress_Layout.addWidget(self.stepLCD)

        LayoutWidget_2 = QWidget(self,"Run_Layout")
        LayoutWidget_2.setGeometry(QRect(11,442,538,32))
        Run_Layout = QHBoxLayout(LayoutWidget_2,0,6,"Run_Layout")

        self.buttonHelp = QPushButton(LayoutWidget_2,"buttonHelp")
        self.buttonHelp.setAutoDefault(1)
        Run_Layout.addWidget(self.buttonHelp)
        Horizontal_Spacing2 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        Run_Layout.addItem(Horizontal_Spacing2)

        self.buttonRun = QPushButton(LayoutWidget_2,"buttonRun")
        self.buttonRun.setAutoDefault(1)
        self.buttonRun.setDefault(1)
        Run_Layout.addWidget(self.buttonRun)

        self.buttonExit = QPushButton(LayoutWidget_2,"buttonExit")
        self.buttonExit.setAutoDefault(1)
        Run_Layout.addWidget(self.buttonExit)

        self.tabWidget = QTabWidget(self,"tabWidget")
        self.tabWidget.setEnabled(1)
        self.tabWidget.setGeometry(QRect(11,6,538,407))
        self.tabWidget.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding,0,0,self.tabWidget.sizePolicy().hasHeightForWidth()))

        self.Widget8 = QWidget(self.tabWidget,"Widget8")

        self.splitter6 = QSplitter(self.Widget8,"splitter6")
        self.splitter6.setGeometry(QRect(10,0,520,360))
        self.splitter6.setOrientation(QSplitter.Vertical)

        self.modSpec = QGroupBox(self.splitter6,"modSpec")
        self.modSpec.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding,0,0,self.modSpec.sizePolicy().hasHeightForWidth()))
        self.modSpec.setMinimumSize(QSize(518,80))

        LayoutWidget_3 = QWidget(self.modSpec,"layout7")
        LayoutWidget_3.setGeometry(QRect(10,20,500,60))
        layout7 = QGridLayout(LayoutWidget_3,1,1,6,6,"layout7")

        self.chooseButton = QPushButton(LayoutWidget_3,"chooseButton")

        layout7.addWidget(self.chooseButton,1,2)

        self.textLabel1 = QLabel(LayoutWidget_3,"textLabel1")

        layout7.addWidget(self.textLabel1,0,0)
        spacer4 = QSpacerItem(370,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout7.addMultiCell(spacer4,0,0,1,3)

        self.scriptNameEdit = QLineEdit(LayoutWidget_3,"scriptNameEdit")
        self.scriptNameEdit.setMargin(1)

        layout7.addMultiCellWidget(self.scriptNameEdit,1,1,0,1)

        self.editButton = QPushButton(LayoutWidget_3,"editButton")

        layout7.addWidget(self.editButton,1,3)

        LayoutWidget_4 = QWidget(self.splitter6,"Database_layout")
        Database_layout = QGridLayout(LayoutWidget_4,1,1,6,6,"Database_layout")
        spacer3 = QSpacerItem(20,100,QSizePolicy.Minimum,QSizePolicy.Expanding)
        Database_layout.addItem(spacer3,1,0)

        self.dbSpecGroupBox = QGroupBox(LayoutWidget_4,"dbSpecGroupBox")
        self.dbSpecGroupBox.setEnabled(0)
        self.dbSpecGroupBox.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.MinimumExpanding,0,0,self.dbSpecGroupBox.sizePolicy().hasHeightForWidth()))

        LayoutWidget_5 = QWidget(self.dbSpecGroupBox,"layout7")
        LayoutWidget_5.setGeometry(QRect(10,20,360,140))
        layout7_2 = QGridLayout(LayoutWidget_5,1,1,6,6,"layout7_2")

        self.textLabel2 = QLabel(LayoutWidget_5,"textLabel2")
        self.textLabel2.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed,0,0,self.textLabel2.sizePolicy().hasHeightForWidth()))

        layout7_2.addWidget(self.textLabel2,0,0)

        self.portEdit = QLineEdit(LayoutWidget_5,"portEdit")

        layout7_2.addWidget(self.portEdit,1,1)

        self.textLabel3 = QLabel(LayoutWidget_5,"textLabel3")
        self.textLabel3.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed,0,0,self.textLabel3.sizePolicy().hasHeightForWidth()))

        layout7_2.addWidget(self.textLabel3,0,1)

        self.pwEdit = QLineEdit(LayoutWidget_5,"pwEdit")
        self.pwEdit.setEchoMode(QLineEdit.Password)

        layout7_2.addWidget(self.pwEdit,3,1)

        self.textLabel1_2 = QLabel(LayoutWidget_5,"textLabel1_2")
        self.textLabel1_2.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed,0,0,self.textLabel1_2.sizePolicy().hasHeightForWidth()))

        layout7_2.addWidget(self.textLabel1_2,2,1)

        self.textLabel4 = QLabel(LayoutWidget_5,"textLabel4")
        self.textLabel4.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed,0,0,self.textLabel4.sizePolicy().hasHeightForWidth()))

        layout7_2.addWidget(self.textLabel4,2,0)

        self.hostnEdit = QLineEdit(LayoutWidget_5,"hostnEdit")

        layout7_2.addWidget(self.hostnEdit,1,0)

        self.uidEdit = QLineEdit(LayoutWidget_5,"uidEdit")

        layout7_2.addWidget(self.uidEdit,3,0)

        Database_layout.addMultiCellWidget(self.dbSpecGroupBox,0,1,1,1)

        layout5 = QVBoxLayout(None,0,6,"layout5")

        self.textLabel1_11 = QLabel(LayoutWidget_4,"textLabel1_11")
        self.textLabel1_11.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred,0,0,self.textLabel1_11.sizePolicy().hasHeightForWidth()))
        layout5.addWidget(self.textLabel1_11)

        self.dbType = QComboBox(0,LayoutWidget_4,"dbType")
        self.dbType.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed,0,0,self.dbType.sizePolicy().hasHeightForWidth()))
        layout5.addWidget(self.dbType)

        Database_layout.addLayout(layout5,0,0)
        self.tabWidget.insertTab(self.Widget8,QString.fromLatin1(""))

        self.Widget9 = QWidget(self.tabWidget,"Widget9")

        LayoutWidget_6 = QWidget(self.Widget9,"layout9")
        LayoutWidget_6.setGeometry(QRect(9,19,294,132))
        layout9 = QGridLayout(LayoutWidget_6,1,1,6,6,"layout9")

        self.unameEdit = QLineEdit(LayoutWidget_6,"unameEdit")

        layout9.addMultiCellWidget(self.unameEdit,0,0,1,3)

        self.textLabel1_5 = QLabel(LayoutWidget_6,"textLabel1_5")

        layout9.addMultiCellWidget(self.textLabel1_5,3,3,0,1)

        self.langCombo = QComboBox(0,LayoutWidget_6,"langCombo")

        layout9.addMultiCellWidget(self.langCombo,3,3,2,3)

        self.textLabel5 = QLabel(LayoutWidget_6,"textLabel5")

        layout9.addWidget(self.textLabel5,1,0)

        self.textLabel2_3 = QLabel(LayoutWidget_6,"textLabel2_3")

        layout9.addMultiCellWidget(self.textLabel2_3,2,2,0,2)

        self.textLabel2_2 = QLabel(LayoutWidget_6,"textLabel2_2")

        layout9.addWidget(self.textLabel2_2,0,0)

        self.editorEdit = QLineEdit(LayoutWidget_6,"editorEdit")

        layout9.addMultiCellWidget(self.editorEdit,1,1,1,3)

        self.pdfEdit = QLineEdit(LayoutWidget_6,"pdfEdit")

        layout9.addWidget(self.pdfEdit,2,3)
        self.tabWidget.insertTab(self.Widget9,QString.fromLatin1(""))

        self.TabPage = QWidget(self.tabWidget,"TabPage")

        self.line1 = QFrame(self.TabPage,"line1")
        self.line1.setGeometry(QRect(289,34,20,320))
        self.line1.setFrameShape(QFrame.VLine)
        self.line1.setFrameShadow(QFrame.Sunken)
        self.line1.setLineWidth(3)
        self.line1.setFrameShape(QFrame.VLine)

        LayoutWidget_7 = QWidget(self.TabPage,"layout14")
        LayoutWidget_7.setGeometry(QRect(0,10,280,350))
        layout14 = QVBoxLayout(LayoutWidget_7,6,6,"layout14")

        self.textLabel5_2 = QLabel(LayoutWidget_7,"textLabel5_2")
        layout14.addWidget(self.textLabel5_2)

        self.textEdit1 = QTextEdit(LayoutWidget_7,"textEdit1")
        layout14.addWidget(self.textEdit1)

        LayoutWidget_8 = QWidget(self.TabPage,"layout18")
        LayoutWidget_8.setGeometry(QRect(320,10,200,349))
        layout18 = QVBoxLayout(LayoutWidget_8,6,6,"layout18")

        layout16 = QVBoxLayout(None,0,6,"layout16")

        layout11 = QVBoxLayout(None,0,6,"layout11")

        self.textLabel1_3 = QLabel(LayoutWidget_8,"textLabel1_3")
        self.textLabel1_3.setAlignment(QLabel.AlignCenter)
        layout11.addWidget(self.textLabel1_3)

        self.dbBackup = QPushButton(LayoutWidget_8,"dbBackup")
        self.dbBackup.setEnabled(0)
        layout11.addWidget(self.dbBackup)

        self.dbInfo = QPushButton(LayoutWidget_8,"dbInfo")
        self.dbInfo.setEnabled(0)
        layout11.addWidget(self.dbInfo)
        layout16.addLayout(layout11)

        self.line2 = QFrame(LayoutWidget_8,"line2")
        self.line2.setFrameShape(QFrame.HLine)
        self.line2.setFrameShadow(QFrame.Sunken)
        self.line2.setLineWidth(2)
        self.line2.setFrameShape(QFrame.HLine)
        layout16.addWidget(self.line2)

        layout15 = QVBoxLayout(None,0,6,"layout15")

        self.textLabel1_4 = QLabel(LayoutWidget_8,"textLabel1_4")
        self.textLabel1_4.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Preferred,0,0,self.textLabel1_4.sizePolicy().hasHeightForWidth()))
        self.textLabel1_4.setMargin(0)
        self.textLabel1_4.setAlignment(QLabel.AlignCenter)
        layout15.addWidget(self.textLabel1_4)

        self.repOpen = QPushButton(LayoutWidget_8,"repOpen")
        layout15.addWidget(self.repOpen)
        layout16.addLayout(layout15)
        layout18.addLayout(layout16)
        spacer6 = QSpacerItem(20,170,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout18.addItem(spacer6)
        self.tabWidget.insertTab(self.TabPage,QString.fromLatin1(""))

        self.visPage = QWidget(self.tabWidget,"visPage")

        LayoutWidget_9 = QWidget(self.visPage,"layout24")
        LayoutWidget_9.setGeometry(QRect(0,279,530,71))
        layout24 = QHBoxLayout(LayoutWidget_9,6,6,"layout24")

        layout23 = QVBoxLayout(None,0,6,"layout23")

        self.textLabel1_9 = QLabel(LayoutWidget_9,"textLabel1_9")
        self.textLabel1_9.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed,0,0,self.textLabel1_9.sizePolicy().hasHeightForWidth()))
        layout23.addWidget(self.textLabel1_9)

        self.consensusButton = QPushButton(LayoutWidget_9,"consensusButton")
        self.consensusButton.setEnabled(0)
        layout23.addWidget(self.consensusButton)
        layout24.addLayout(layout23)
        spacer8 = QSpacerItem(260,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout24.addItem(spacer8)

        LayoutWidget_10 = QWidget(self.visPage,"layout20")
        LayoutWidget_10.setGeometry(QRect(0,10,265,263))
        layout20 = QVBoxLayout(LayoutWidget_10,6,6,"layout20")

        self.textLabel1_7 = QLabel(LayoutWidget_10,"textLabel1_7")
        self.textLabel1_7.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed,0,0,self.textLabel1_7.sizePolicy().hasHeightForWidth()))
        layout20.addWidget(self.textLabel1_7)

        self.tableList = QComboBox(0,LayoutWidget_10,"tableList")
        layout20.addWidget(self.tableList)

        self.textLabel1_10 = QLabel(LayoutWidget_10,"textLabel1_10")
        self.textLabel1_10.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed,0,0,self.textLabel1_10.sizePolicy().hasHeightForWidth()))
        layout20.addWidget(self.textLabel1_10)

        self.variableList = QComboBox(0,LayoutWidget_10,"variableList")
        layout20.addWidget(self.variableList)

        self.textLabel2_4 = QLabel(LayoutWidget_10,"textLabel2_4")
        self.textLabel2_4.setEnabled(1)
        self.textLabel2_4.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed,0,0,self.textLabel2_4.sizePolicy().hasHeightForWidth()))
        layout20.addWidget(self.textLabel2_4)

        self.mapList = QComboBox(0,LayoutWidget_10,"mapList")
        self.mapList.setEnabled(1)
        layout20.addWidget(self.mapList)

        LayoutWidget_11 = QWidget(self.visPage,"layout19")
        LayoutWidget_11.setGeometry(QRect(272,11,260,261))
        layout19 = QVBoxLayout(LayoutWidget_11,6,6,"layout19")

        self.dbscanButton = QPushButton(LayoutWidget_11,"dbscanButton")
        layout19.addWidget(self.dbscanButton)

        self.textLabel1_8 = QLabel(LayoutWidget_11,"textLabel1_8")
        self.textLabel1_8.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed,0,0,self.textLabel1_8.sizePolicy().hasHeightForWidth()))
        layout19.addWidget(self.textLabel1_8)

        self.rateSpinBox = QSpinBox(LayoutWidget_11,"rateSpinBox")
        self.rateSpinBox.setMinValue(20)
        layout19.addWidget(self.rateSpinBox)
        spacer7 = QSpacerItem(20,90,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout19.addItem(spacer7)

        self.playButton_2D = QPushButton(LayoutWidget_11,"playButton_2D")
        self.playButton_2D.setEnabled(0)
        layout19.addWidget(self.playButton_2D)

        self.playButton = QPushButton(LayoutWidget_11,"playButton")
        layout19.addWidget(self.playButton)
        self.tabWidget.insertTab(self.visPage,QString.fromLatin1(""))

        self.languageChange()

        self.resize(QSize(560,480).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("Epigrass Control Panel"))
        self.textLabel1_6.setText(self.__tr("Progress:"))
        QToolTip.add(self.stepLCD,self.__tr("Simulation step"))
        self.buttonHelp.setText(self.__tr("&Help"))
        self.buttonHelp.setAccel(QKeySequence(self.__tr("F1")))
        QToolTip.add(self.buttonHelp,self.__tr("Click here to open the userguide in the web browser"))
        self.buttonRun.setText(self.__tr("&Run"))
        self.buttonRun.setAccel(QKeySequence(self.__tr("Alt+R")))
        QToolTip.add(self.buttonRun,self.__tr("Click here to start your simulation"))
        self.buttonExit.setText(self.__tr("&Exit"))
        self.buttonExit.setAccel(QKeySequence(self.__tr("Alt+E")))
        QToolTip.add(self.buttonExit,self.__tr("Click here to leave Epigrass"))
        QToolTip.add(self.tabWidget,QString.null)
        self.modSpec.setTitle(self.__tr("Model Specification"))
        self.chooseButton.setText(self.__tr("Choose"))
        self.textLabel1.setText(self.__tr("Script Name:"))
        QToolTip.add(self.scriptNameEdit,self.__tr("write the name of the your script or press the choose button on the right to select one."))
        self.editButton.setText(self.__tr("Edit"))
        self.dbSpecGroupBox.setTitle(self.__tr("Database Specification"))
        self.textLabel2.setText(self.__tr("Host:"))
        self.portEdit.setText(self.__tr("3306"))
        QToolTip.add(self.portEdit,self.__tr("Enter the port  the server listens to."))
        self.textLabel3.setText(self.__tr("Port:"))
        QToolTip.add(self.pwEdit,self.__tr("Database password for the userid entered"))
        self.textLabel1_2.setText(self.__tr("Password:"))
        self.textLabel4.setText(self.__tr("Userid:"))
        self.hostnEdit.setText(self.__tr("localhost"))
        QToolTip.add(self.hostnEdit,self.__tr("This is the url of your database server."))
        QToolTip.add(self.uidEdit,self.__tr("This is the userid for accessing the database server"))
        self.textLabel1_11.setText(self.__tr("Database type:"))
        self.dbType.clear()
        self.dbType.insertItem(self.__tr("MySQL"))
        self.dbType.insertItem(self.__tr("SQLite"))
        self.dbType.insertItem(self.__tr("CSV"))
        self.dbType.setCurrentItem(1)
        QToolTip.add(self.dbType,self.__tr("Select your database type"))
        self.tabWidget.changeTab(self.Widget8,self.__tr("Run Options"))
        QToolTip.add(self.unameEdit,self.__tr("Enter your full name. This will be added to the report."))
        self.textLabel1_5.setText(self.__tr("Language"))
        self.langCombo.clear()
        self.langCombo.insertItem(self.__tr("English"))
        self.langCombo.insertItem(self.__tr("Brazilian portuguese"))
        self.langCombo.insertItem(self.__tr("French"))
        QToolTip.add(self.langCombo,self.__tr("Select the language for the GUI"))
        self.textLabel5.setText(self.__tr("Editor"))
        self.textLabel2_3.setText(self.__tr("PDF Viewer"))
        self.textLabel2_2.setText(self.__tr("Name"))
        QToolTip.add(self.editorEdit,self.__tr("Enter your preferred text editor"))
        self.pdfEdit.setText(QString.null)
        QToolTip.add(self.pdfEdit,self.__tr("Enter the name of your preferred PDF viewer"))
        self.tabWidget.changeTab(self.Widget9,self.__tr("Settings"))
        self.textLabel5_2.setText(self.__tr("Simulation Status"))
        self.textLabel1_3.setText(self.__tr("Database"))
        self.dbBackup.setText(self.__tr("Backup"))
        QToolTip.add(self.dbBackup,self.__tr("Click here to backup the epigrass database "))
        self.dbInfo.setText(self.__tr("Info"))
        QToolTip.add(self.dbInfo,self.__tr("Click here for a short description of the epigrass database"))
        self.textLabel1_4.setText(self.__tr("Report"))
        self.repOpen.setText(self.__tr("Open"))
        self.tabWidget.changeTab(self.TabPage,self.__tr("Utilities"))
        self.textLabel1_9.setText(self.__tr("Spread Trees"))
        self.consensusButton.setText(self.__tr("Consensus Tree"))
        QToolTip.add(self.consensusButton,self.__tr("Select a directory with tree-files to build consensus on."))
        self.textLabel1_7.setText(self.__tr("Simulations stored:"))
        QToolTip.add(self.tableList,self.__tr("Select a database stored simulation"))
        self.textLabel1_10.setText(self.__tr("Variable to display:"))
        QToolTip.add(self.variableList,self.__tr("Select a variable to display in the animation"))
        self.textLabel2_4.setText(self.__tr("Maps available:"))
        self.mapList.clear()
        self.mapList.insertItem(self.__tr("No map"))
        QToolTip.add(self.mapList,self.__tr("Select a map"))
        self.dbscanButton.setText(self.__tr("Scan DB"))
        self.textLabel1_8.setText(self.__tr("Animation rate"))
        self.playButton_2D.setText(self.__tr("Start 2D animation"))
        self.playButton.setText(self.__tr("Start 3D animation"))
        self.tabWidget.changeTab(self.visPage,self.__tr("Visualization"))


    def Main_layout_destroyed(self,a0):
        print "MainPanel.Main_layout_destroyed(QObject*): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("MainPanel",s,c)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = MainPanel()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
