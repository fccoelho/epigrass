# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/flavio/Documents/Projetos/Epigrass/Epigrass-devel-qt4/cpanel4new.ui'
#
# Created: Wed Jul  9 13:12:46 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(QtCore.QSize(QtCore.QRect(0,0,807,479).size()).expandedTo(MainWindow.minimumSizeHint()))
        MainWindow.setMaximumSize(QtCore.QSize(16777215,479))

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setGeometry(QtCore.QRect(0,31,807,420))
        self.centralwidget.setObjectName("centralwidget")

        self.vboxlayout = QtGui.QVBoxLayout(self.centralwidget)
        self.vboxlayout.setObjectName("vboxlayout")

        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setEnabled(True)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.tabWidget.setObjectName("tabWidget")

        self.Widget8 = QtGui.QWidget()
        self.Widget8.setGeometry(QtCore.QRect(0,0,787,298))
        self.Widget8.setObjectName("Widget8")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.Widget8)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.splitter6 = QtGui.QSplitter(self.Widget8)
        self.splitter6.setOrientation(QtCore.Qt.Vertical)
        self.splitter6.setObjectName("splitter6")

        self.modSpec = QtGui.QGroupBox(self.splitter6)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.modSpec.sizePolicy().hasHeightForWidth())
        self.modSpec.setSizePolicy(sizePolicy)
        self.modSpec.setMinimumSize(QtCore.QSize(518,80))
        self.modSpec.setObjectName("modSpec")

        self.gridlayout = QtGui.QGridLayout(self.modSpec)
        self.gridlayout.setObjectName("gridlayout")

        self.gridlayout1 = QtGui.QGridLayout()
        self.gridlayout1.setObjectName("gridlayout1")

        self.chooseButton = QtGui.QPushButton(self.modSpec)
        self.chooseButton.setObjectName("chooseButton")
        self.gridlayout1.addWidget(self.chooseButton,1,2,1,1)

        self.textLabel1 = QtGui.QLabel(self.modSpec)
        self.textLabel1.setWordWrap(False)
        self.textLabel1.setObjectName("textLabel1")
        self.gridlayout1.addWidget(self.textLabel1,0,0,1,1)

        spacerItem = QtGui.QSpacerItem(370,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout1.addItem(spacerItem,0,1,1,3)

        self.scriptNameEdit = QtGui.QLineEdit(self.modSpec)
        self.scriptNameEdit.setObjectName("scriptNameEdit")
        self.gridlayout1.addWidget(self.scriptNameEdit,1,0,1,2)

        self.editButton = QtGui.QPushButton(self.modSpec)
        self.editButton.setObjectName("editButton")
        self.gridlayout1.addWidget(self.editButton,1,3,1,1)
        self.gridlayout.addLayout(self.gridlayout1,0,0,1,1)

        self.Database_layout = QtGui.QWidget(self.splitter6)
        self.Database_layout.setObjectName("Database_layout")

        self.gridlayout2 = QtGui.QGridLayout(self.Database_layout)
        self.gridlayout2.setObjectName("gridlayout2")

        spacerItem1 = QtGui.QSpacerItem(20,100,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout2.addItem(spacerItem1,1,0,1,1)

        self.dbSpecGroupBox = QtGui.QGroupBox(self.Database_layout)
        self.dbSpecGroupBox.setEnabled(False)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dbSpecGroupBox.sizePolicy().hasHeightForWidth())
        self.dbSpecGroupBox.setSizePolicy(sizePolicy)
        self.dbSpecGroupBox.setObjectName("dbSpecGroupBox")

        self.layout7_2 = QtGui.QWidget(self.dbSpecGroupBox)
        self.layout7_2.setGeometry(QtCore.QRect(10,20,360,140))
        self.layout7_2.setObjectName("layout7_2")

        self.gridlayout3 = QtGui.QGridLayout(self.layout7_2)
        self.gridlayout3.setObjectName("gridlayout3")

        self.textLabel2 = QtGui.QLabel(self.layout7_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel2.sizePolicy().hasHeightForWidth())
        self.textLabel2.setSizePolicy(sizePolicy)
        self.textLabel2.setWordWrap(False)
        self.textLabel2.setObjectName("textLabel2")
        self.gridlayout3.addWidget(self.textLabel2,0,0,1,1)

        self.portEdit = QtGui.QLineEdit(self.layout7_2)
        self.portEdit.setObjectName("portEdit")
        self.gridlayout3.addWidget(self.portEdit,1,1,1,1)

        self.textLabel3 = QtGui.QLabel(self.layout7_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel3.sizePolicy().hasHeightForWidth())
        self.textLabel3.setSizePolicy(sizePolicy)
        self.textLabel3.setWordWrap(False)
        self.textLabel3.setObjectName("textLabel3")
        self.gridlayout3.addWidget(self.textLabel3,0,1,1,1)

        self.pwEdit = QtGui.QLineEdit(self.layout7_2)
        self.pwEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.pwEdit.setObjectName("pwEdit")
        self.gridlayout3.addWidget(self.pwEdit,3,1,1,1)

        self.textLabel1_2 = QtGui.QLabel(self.layout7_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel1_2.sizePolicy().hasHeightForWidth())
        self.textLabel1_2.setSizePolicy(sizePolicy)
        self.textLabel1_2.setWordWrap(False)
        self.textLabel1_2.setObjectName("textLabel1_2")
        self.gridlayout3.addWidget(self.textLabel1_2,2,1,1,1)

        self.textLabel4 = QtGui.QLabel(self.layout7_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel4.sizePolicy().hasHeightForWidth())
        self.textLabel4.setSizePolicy(sizePolicy)
        self.textLabel4.setWordWrap(False)
        self.textLabel4.setObjectName("textLabel4")
        self.gridlayout3.addWidget(self.textLabel4,2,0,1,1)

        self.hostnEdit = QtGui.QLineEdit(self.layout7_2)
        self.hostnEdit.setObjectName("hostnEdit")
        self.gridlayout3.addWidget(self.hostnEdit,1,0,1,1)

        self.uidEdit = QtGui.QLineEdit(self.layout7_2)
        self.uidEdit.setObjectName("uidEdit")
        self.gridlayout3.addWidget(self.uidEdit,3,0,1,1)
        self.gridlayout2.addWidget(self.dbSpecGroupBox,0,1,2,1)

        self.vboxlayout2 = QtGui.QVBoxLayout()
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.textLabel1_11 = QtGui.QLabel(self.Database_layout)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel1_11.sizePolicy().hasHeightForWidth())
        self.textLabel1_11.setSizePolicy(sizePolicy)
        self.textLabel1_11.setWordWrap(False)
        self.textLabel1_11.setObjectName("textLabel1_11")
        self.vboxlayout2.addWidget(self.textLabel1_11)

        self.dbType = QtGui.QComboBox(self.Database_layout)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dbType.sizePolicy().hasHeightForWidth())
        self.dbType.setSizePolicy(sizePolicy)
        self.dbType.setObjectName("dbType")
        self.vboxlayout2.addWidget(self.dbType)
        self.gridlayout2.addLayout(self.vboxlayout2,0,0,1,1)
        self.vboxlayout1.addWidget(self.splitter6)
        self.tabWidget.addTab(self.Widget8,"")

        self.Widget9 = QtGui.QWidget()
        self.Widget9.setGeometry(QtCore.QRect(0,0,787,298))
        self.Widget9.setObjectName("Widget9")

        self.layout9 = QtGui.QWidget(self.Widget9)
        self.layout9.setGeometry(QtCore.QRect(9,19,304,153))
        self.layout9.setObjectName("layout9")

        self.gridlayout4 = QtGui.QGridLayout(self.layout9)
        self.gridlayout4.setObjectName("gridlayout4")

        self.unameEdit = QtGui.QLineEdit(self.layout9)
        self.unameEdit.setObjectName("unameEdit")
        self.gridlayout4.addWidget(self.unameEdit,0,1,1,3)

        self.textLabel1_5 = QtGui.QLabel(self.layout9)
        self.textLabel1_5.setWordWrap(False)
        self.textLabel1_5.setObjectName("textLabel1_5")
        self.gridlayout4.addWidget(self.textLabel1_5,3,0,1,2)

        self.langCombo = QtGui.QComboBox(self.layout9)
        self.langCombo.setObjectName("langCombo")
        self.gridlayout4.addWidget(self.langCombo,3,2,1,2)

        self.textLabel5 = QtGui.QLabel(self.layout9)
        self.textLabel5.setWordWrap(False)
        self.textLabel5.setObjectName("textLabel5")
        self.gridlayout4.addWidget(self.textLabel5,1,0,1,1)

        self.textLabel2_3 = QtGui.QLabel(self.layout9)
        self.textLabel2_3.setWordWrap(False)
        self.textLabel2_3.setObjectName("textLabel2_3")
        self.gridlayout4.addWidget(self.textLabel2_3,2,0,1,3)

        self.textLabel2_2 = QtGui.QLabel(self.layout9)
        self.textLabel2_2.setWordWrap(False)
        self.textLabel2_2.setObjectName("textLabel2_2")
        self.gridlayout4.addWidget(self.textLabel2_2,0,0,1,1)

        self.editorEdit = QtGui.QLineEdit(self.layout9)
        self.editorEdit.setObjectName("editorEdit")
        self.gridlayout4.addWidget(self.editorEdit,1,1,1,3)

        self.pdfEdit = QtGui.QLineEdit(self.layout9)
        self.pdfEdit.setObjectName("pdfEdit")
        self.gridlayout4.addWidget(self.pdfEdit,2,3,1,1)
        self.tabWidget.addTab(self.Widget9,"")

        self.TabPage = QtGui.QWidget()
        self.TabPage.setGeometry(QtCore.QRect(0,0,787,298))
        self.TabPage.setObjectName("TabPage")

        self.hboxlayout = QtGui.QHBoxLayout(self.TabPage)
        self.hboxlayout.setObjectName("hboxlayout")

        self.vboxlayout3 = QtGui.QVBoxLayout()
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.textLabel5_2 = QtGui.QLabel(self.TabPage)
        self.textLabel5_2.setWordWrap(False)
        self.textLabel5_2.setObjectName("textLabel5_2")
        self.vboxlayout3.addWidget(self.textLabel5_2)

        self.textEdit1 = QtGui.QTextEdit(self.TabPage)
        self.textEdit1.setObjectName("textEdit1")
        self.vboxlayout3.addWidget(self.textEdit1)
        self.hboxlayout.addLayout(self.vboxlayout3)

        self.line1 = QtGui.QFrame(self.TabPage)
        self.line1.setFrameShape(QtGui.QFrame.VLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.line1.setLineWidth(3)
        self.line1.setObjectName("line1")
        self.hboxlayout.addWidget(self.line1)

        self.vboxlayout4 = QtGui.QVBoxLayout()
        self.vboxlayout4.setObjectName("vboxlayout4")

        self.vboxlayout5 = QtGui.QVBoxLayout()
        self.vboxlayout5.setObjectName("vboxlayout5")

        self.vboxlayout6 = QtGui.QVBoxLayout()
        self.vboxlayout6.setObjectName("vboxlayout6")

        self.textLabel1_3 = QtGui.QLabel(self.TabPage)
        self.textLabel1_3.setAlignment(QtCore.Qt.AlignCenter)
        self.textLabel1_3.setWordWrap(False)
        self.textLabel1_3.setObjectName("textLabel1_3")
        self.vboxlayout6.addWidget(self.textLabel1_3)

        self.dbBackup = QtGui.QPushButton(self.TabPage)
        self.dbBackup.setEnabled(False)
        self.dbBackup.setObjectName("dbBackup")
        self.vboxlayout6.addWidget(self.dbBackup)

        self.dbInfo = QtGui.QPushButton(self.TabPage)
        self.dbInfo.setEnabled(False)
        self.dbInfo.setObjectName("dbInfo")
        self.vboxlayout6.addWidget(self.dbInfo)
        self.vboxlayout5.addLayout(self.vboxlayout6)

        self.line2 = QtGui.QFrame(self.TabPage)
        self.line2.setFrameShape(QtGui.QFrame.HLine)
        self.line2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line2.setLineWidth(2)
        self.line2.setObjectName("line2")
        self.vboxlayout5.addWidget(self.line2)

        self.vboxlayout7 = QtGui.QVBoxLayout()
        self.vboxlayout7.setObjectName("vboxlayout7")

        self.textLabel1_4 = QtGui.QLabel(self.TabPage)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel1_4.sizePolicy().hasHeightForWidth())
        self.textLabel1_4.setSizePolicy(sizePolicy)
        self.textLabel1_4.setAlignment(QtCore.Qt.AlignCenter)
        self.textLabel1_4.setWordWrap(False)
        self.textLabel1_4.setMargin(0)
        self.textLabel1_4.setObjectName("textLabel1_4")
        self.vboxlayout7.addWidget(self.textLabel1_4)

        self.repOpen = QtGui.QPushButton(self.TabPage)
        self.repOpen.setObjectName("repOpen")
        self.vboxlayout7.addWidget(self.repOpen)
        self.vboxlayout5.addLayout(self.vboxlayout7)
        self.vboxlayout4.addLayout(self.vboxlayout5)

        spacerItem2 = QtGui.QSpacerItem(20,170,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout4.addItem(spacerItem2)
        self.hboxlayout.addLayout(self.vboxlayout4)
        self.tabWidget.addTab(self.TabPage,"")

        self.visPage = QtGui.QWidget()
        self.visPage.setGeometry(QtCore.QRect(0,0,787,298))
        self.visPage.setObjectName("visPage")

        self.gridlayout5 = QtGui.QGridLayout(self.visPage)
        self.gridlayout5.setObjectName("gridlayout5")

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.vboxlayout8 = QtGui.QVBoxLayout()
        self.vboxlayout8.setObjectName("vboxlayout8")

        self.textLabel1_9 = QtGui.QLabel(self.visPage)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel1_9.sizePolicy().hasHeightForWidth())
        self.textLabel1_9.setSizePolicy(sizePolicy)
        self.textLabel1_9.setWordWrap(False)
        self.textLabel1_9.setObjectName("textLabel1_9")
        self.vboxlayout8.addWidget(self.textLabel1_9)

        self.consensusButton = QtGui.QPushButton(self.visPage)
        self.consensusButton.setEnabled(False)
        self.consensusButton.setObjectName("consensusButton")
        self.vboxlayout8.addWidget(self.consensusButton)
        self.hboxlayout1.addLayout(self.vboxlayout8)

        spacerItem3 = QtGui.QSpacerItem(260,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem3)
        self.gridlayout5.addLayout(self.hboxlayout1,1,0,1,1)

        self.splitter = QtGui.QSplitter(self.visPage)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        self.layout20 = QtGui.QWidget(self.splitter)
        self.layout20.setObjectName("layout20")

        self.vboxlayout9 = QtGui.QVBoxLayout(self.layout20)
        self.vboxlayout9.setObjectName("vboxlayout9")

        self.textLabel1_7 = QtGui.QLabel(self.layout20)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel1_7.sizePolicy().hasHeightForWidth())
        self.textLabel1_7.setSizePolicy(sizePolicy)
        self.textLabel1_7.setWordWrap(False)
        self.textLabel1_7.setObjectName("textLabel1_7")
        self.vboxlayout9.addWidget(self.textLabel1_7)

        self.tableList = QtGui.QComboBox(self.layout20)
        self.tableList.setObjectName("tableList")
        self.vboxlayout9.addWidget(self.tableList)

        self.textLabel1_10 = QtGui.QLabel(self.layout20)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel1_10.sizePolicy().hasHeightForWidth())
        self.textLabel1_10.setSizePolicy(sizePolicy)
        self.textLabel1_10.setWordWrap(False)
        self.textLabel1_10.setObjectName("textLabel1_10")
        self.vboxlayout9.addWidget(self.textLabel1_10)

        self.variableList = QtGui.QComboBox(self.layout20)
        self.variableList.setObjectName("variableList")
        self.vboxlayout9.addWidget(self.variableList)

        self.textLabel2_4 = QtGui.QLabel(self.layout20)
        self.textLabel2_4.setEnabled(True)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel2_4.sizePolicy().hasHeightForWidth())
        self.textLabel2_4.setSizePolicy(sizePolicy)
        self.textLabel2_4.setWordWrap(False)
        self.textLabel2_4.setObjectName("textLabel2_4")
        self.vboxlayout9.addWidget(self.textLabel2_4)

        self.mapList = QtGui.QComboBox(self.layout20)
        self.mapList.setEnabled(True)
        self.mapList.setObjectName("mapList")
        self.vboxlayout9.addWidget(self.mapList)

        self.layout19 = QtGui.QWidget(self.splitter)
        self.layout19.setObjectName("layout19")

        self.vboxlayout10 = QtGui.QVBoxLayout(self.layout19)
        self.vboxlayout10.setObjectName("vboxlayout10")

        self.dbscanButton = QtGui.QPushButton(self.layout19)
        self.dbscanButton.setObjectName("dbscanButton")
        self.vboxlayout10.addWidget(self.dbscanButton)

        self.textLabel1_8 = QtGui.QLabel(self.layout19)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel1_8.sizePolicy().hasHeightForWidth())
        self.textLabel1_8.setSizePolicy(sizePolicy)
        self.textLabel1_8.setWordWrap(False)
        self.textLabel1_8.setObjectName("textLabel1_8")
        self.vboxlayout10.addWidget(self.textLabel1_8)

        self.rateSpinBox = QtGui.QSpinBox(self.layout19)
        self.rateSpinBox.setMinimum(1)
        self.rateSpinBox.setMaximum(5)
        self.rateSpinBox.setObjectName("rateSpinBox")
        self.vboxlayout10.addWidget(self.rateSpinBox)

        spacerItem4 = QtGui.QSpacerItem(20,90,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout10.addItem(spacerItem4)

        self.playButton = QtGui.QPushButton(self.layout19)
        self.playButton.setObjectName("playButton")
        self.vboxlayout10.addWidget(self.playButton)
        self.gridlayout5.addWidget(self.splitter,0,0,1,1)
        self.tabWidget.addTab(self.visPage,"")
        self.vboxlayout.addWidget(self.tabWidget)

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.textLabel1_6 = QtGui.QLabel(self.centralwidget)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel1_6.sizePolicy().hasHeightForWidth())
        self.textLabel1_6.setSizePolicy(sizePolicy)
        self.textLabel1_6.setWordWrap(False)
        self.textLabel1_6.setObjectName("textLabel1_6")
        self.hboxlayout2.addWidget(self.textLabel1_6)

        self.stepLCD = QtGui.QLCDNumber(self.centralwidget)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stepLCD.sizePolicy().hasHeightForWidth())
        self.stepLCD.setSizePolicy(sizePolicy)
        self.stepLCD.setObjectName("stepLCD")
        self.hboxlayout2.addWidget(self.stepLCD)
        self.vboxlayout.addLayout(self.hboxlayout2)

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setSpacing(6)
        self.hboxlayout3.setMargin(0)
        self.hboxlayout3.setObjectName("hboxlayout3")

        self.buttonHelp = QtGui.QPushButton(self.centralwidget)
        self.buttonHelp.setAutoDefault(True)
        self.buttonHelp.setObjectName("buttonHelp")
        self.hboxlayout3.addWidget(self.buttonHelp)

        spacerItem5 = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout3.addItem(spacerItem5)

        self.buttonRun = QtGui.QPushButton(self.centralwidget)
        self.buttonRun.setAutoDefault(True)
        self.buttonRun.setDefault(True)
        self.buttonRun.setObjectName("buttonRun")
        self.hboxlayout3.addWidget(self.buttonRun)

        self.buttonExit = QtGui.QPushButton(self.centralwidget)
        self.buttonExit.setAutoDefault(True)
        self.buttonExit.setObjectName("buttonExit")
        self.hboxlayout3.addWidget(self.buttonExit)
        self.vboxlayout.addLayout(self.hboxlayout3)
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,807,31))
        self.menubar.setObjectName("menubar")

        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")

        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setGeometry(QtCore.QRect(0,451,807,28))
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.dbType.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Epigrass", None, QtGui.QApplication.UnicodeUTF8))
        self.modSpec.setTitle(QtGui.QApplication.translate("MainWindow", "Model Specification", None, QtGui.QApplication.UnicodeUTF8))
        self.chooseButton.setText(QtGui.QApplication.translate("MainWindow", "Choose", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1.setText(QtGui.QApplication.translate("MainWindow", "Script Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.scriptNameEdit.setToolTip(QtGui.QApplication.translate("MainWindow", "write the name of the your script or press the choose button on the right to select one.", None, QtGui.QApplication.UnicodeUTF8))
        self.editButton.setText(QtGui.QApplication.translate("MainWindow", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.dbSpecGroupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Database Specification", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2.setText(QtGui.QApplication.translate("MainWindow", "Host:", None, QtGui.QApplication.UnicodeUTF8))
        self.portEdit.setToolTip(QtGui.QApplication.translate("MainWindow", "Enter the port  the server listens to.", None, QtGui.QApplication.UnicodeUTF8))
        self.portEdit.setText(QtGui.QApplication.translate("MainWindow", "3306", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel3.setText(QtGui.QApplication.translate("MainWindow", "Port:", None, QtGui.QApplication.UnicodeUTF8))
        self.pwEdit.setToolTip(QtGui.QApplication.translate("MainWindow", "Database password for the userid entered", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2.setText(QtGui.QApplication.translate("MainWindow", "Password:", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel4.setText(QtGui.QApplication.translate("MainWindow", "Userid:", None, QtGui.QApplication.UnicodeUTF8))
        self.hostnEdit.setToolTip(QtGui.QApplication.translate("MainWindow", "This is the url of your database server.", None, QtGui.QApplication.UnicodeUTF8))
        self.hostnEdit.setText(QtGui.QApplication.translate("MainWindow", "localhost", None, QtGui.QApplication.UnicodeUTF8))
        self.uidEdit.setToolTip(QtGui.QApplication.translate("MainWindow", "This is the userid for accessing the database server", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_11.setText(QtGui.QApplication.translate("MainWindow", "Database type:", None, QtGui.QApplication.UnicodeUTF8))
        self.dbType.setToolTip(QtGui.QApplication.translate("MainWindow", "Select your database type", None, QtGui.QApplication.UnicodeUTF8))
        self.dbType.addItem(QtGui.QApplication.translate("MainWindow", "MySQL", None, QtGui.QApplication.UnicodeUTF8))
        self.dbType.addItem(QtGui.QApplication.translate("MainWindow", "SQLite", None, QtGui.QApplication.UnicodeUTF8))
        self.dbType.addItem(QtGui.QApplication.translate("MainWindow", "CSV", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Widget8), QtGui.QApplication.translate("MainWindow", "Run Options", None, QtGui.QApplication.UnicodeUTF8))
        self.unameEdit.setToolTip(QtGui.QApplication.translate("MainWindow", "Enter your full name. This will be added to the report.", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_5.setText(QtGui.QApplication.translate("MainWindow", "Language", None, QtGui.QApplication.UnicodeUTF8))
        self.langCombo.setToolTip(QtGui.QApplication.translate("MainWindow", "Select the language for the GUI", None, QtGui.QApplication.UnicodeUTF8))
        self.langCombo.addItem(QtGui.QApplication.translate("MainWindow", "English", None, QtGui.QApplication.UnicodeUTF8))
        self.langCombo.addItem(QtGui.QApplication.translate("MainWindow", "Brazilian portuguese", None, QtGui.QApplication.UnicodeUTF8))
        self.langCombo.addItem(QtGui.QApplication.translate("MainWindow", "French", None, QtGui.QApplication.UnicodeUTF8))
        self.langCombo.addItem(QtGui.QApplication.translate("MainWindow", "Spanish", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel5.setText(QtGui.QApplication.translate("MainWindow", "Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2_3.setText(QtGui.QApplication.translate("MainWindow", "PDF Viewer", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2_2.setText(QtGui.QApplication.translate("MainWindow", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.editorEdit.setToolTip(QtGui.QApplication.translate("MainWindow", "Enter your preferred text editor", None, QtGui.QApplication.UnicodeUTF8))
        self.pdfEdit.setToolTip(QtGui.QApplication.translate("MainWindow", "Enter the name of your preferred PDF viewer", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Widget9), QtGui.QApplication.translate("MainWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel5_2.setText(QtGui.QApplication.translate("MainWindow", "Simulation Status", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_3.setText(QtGui.QApplication.translate("MainWindow", "Database", None, QtGui.QApplication.UnicodeUTF8))
        self.dbBackup.setToolTip(QtGui.QApplication.translate("MainWindow", "Click here to backup the epigrass database ", None, QtGui.QApplication.UnicodeUTF8))
        self.dbBackup.setText(QtGui.QApplication.translate("MainWindow", "Backup", None, QtGui.QApplication.UnicodeUTF8))
        self.dbInfo.setToolTip(QtGui.QApplication.translate("MainWindow", "Click here for a short description of the epigrass database", None, QtGui.QApplication.UnicodeUTF8))
        self.dbInfo.setText(QtGui.QApplication.translate("MainWindow", "Info", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_4.setText(QtGui.QApplication.translate("MainWindow", "Report", None, QtGui.QApplication.UnicodeUTF8))
        self.repOpen.setText(QtGui.QApplication.translate("MainWindow", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.TabPage), QtGui.QApplication.translate("MainWindow", "Utilities", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_9.setText(QtGui.QApplication.translate("MainWindow", "Spread Trees", None, QtGui.QApplication.UnicodeUTF8))
        self.consensusButton.setToolTip(QtGui.QApplication.translate("MainWindow", "Select a directory with tree-files to build consensus on.", None, QtGui.QApplication.UnicodeUTF8))
        self.consensusButton.setText(QtGui.QApplication.translate("MainWindow", "Consensus Tree", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_7.setText(QtGui.QApplication.translate("MainWindow", "Simulations stored:", None, QtGui.QApplication.UnicodeUTF8))
        self.tableList.setToolTip(QtGui.QApplication.translate("MainWindow", "Select a database stored simulation", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_10.setText(QtGui.QApplication.translate("MainWindow", "Variable to display:", None, QtGui.QApplication.UnicodeUTF8))
        self.variableList.setToolTip(QtGui.QApplication.translate("MainWindow", "Select a variable to display in the animation", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2_4.setText(QtGui.QApplication.translate("MainWindow", "Maps available:", None, QtGui.QApplication.UnicodeUTF8))
        self.mapList.setToolTip(QtGui.QApplication.translate("MainWindow", "Select a map", None, QtGui.QApplication.UnicodeUTF8))
        self.mapList.addItem(QtGui.QApplication.translate("MainWindow", "No map", None, QtGui.QApplication.UnicodeUTF8))
        self.dbscanButton.setText(QtGui.QApplication.translate("MainWindow", "Scan DB", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_8.setText(QtGui.QApplication.translate("MainWindow", "Animation rate", None, QtGui.QApplication.UnicodeUTF8))
        self.rateSpinBox.setToolTip(QtGui.QApplication.translate("MainWindow", "Time steps per second", None, QtGui.QApplication.UnicodeUTF8))
        self.playButton.setText(QtGui.QApplication.translate("MainWindow", "Start animation", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.visPage), QtGui.QApplication.translate("MainWindow", "Visualization", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_6.setText(QtGui.QApplication.translate("MainWindow", "Progress:", None, QtGui.QApplication.UnicodeUTF8))
        self.stepLCD.setToolTip(QtGui.QApplication.translate("MainWindow", "Simulation step", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonHelp.setToolTip(QtGui.QApplication.translate("MainWindow", "Click here to open the userguide in the web browser", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonHelp.setText(QtGui.QApplication.translate("MainWindow", "&Help", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonHelp.setShortcut(QtGui.QApplication.translate("MainWindow", "F1", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonRun.setToolTip(QtGui.QApplication.translate("MainWindow", "Click here to start your simulation", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonRun.setText(QtGui.QApplication.translate("MainWindow", "&Run", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonRun.setShortcut(QtGui.QApplication.translate("MainWindow", "Alt+R", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonExit.setToolTip(QtGui.QApplication.translate("MainWindow", "Click here to leave Epigrass", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonExit.setText(QtGui.QApplication.translate("MainWindow", "&Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonExit.setShortcut(QtGui.QApplication.translate("MainWindow", "Alt+E", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("MainWindow", "Help", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
