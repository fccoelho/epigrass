# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/flavio/Documents/Projetos/Epigrass/Epigrass-devel-qt4/cpanel4.ui'
#
# Created: Fri Jun 20 10:23:38 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainPanel(object):
    def setupUi(self, MainPanel):
        MainPanel.setObjectName("MainPanel")
        MainPanel.resize(QtCore.QSize(QtCore.QRect(0,0,561,480).size()).expandedTo(MainPanel.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainPanel.sizePolicy().hasHeightForWidth())
        MainPanel.setSizePolicy(sizePolicy)
        MainPanel.setMinimumSize(QtCore.QSize(560,480))

        self.progress_Layout = QtGui.QWidget(MainPanel)
        self.progress_Layout.setGeometry(QtCore.QRect(11,415,538,25))
        self.progress_Layout.setObjectName("progress_Layout")

        self.hboxlayout = QtGui.QHBoxLayout(self.progress_Layout)
        self.hboxlayout.setObjectName("hboxlayout")

        self.textLabel1_6 = QtGui.QLabel(self.progress_Layout)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel1_6.sizePolicy().hasHeightForWidth())
        self.textLabel1_6.setSizePolicy(sizePolicy)
        self.textLabel1_6.setWordWrap(False)
        self.textLabel1_6.setObjectName("textLabel1_6")
        self.hboxlayout.addWidget(self.textLabel1_6)

        self.stepLCD = QtGui.QLCDNumber(self.progress_Layout)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stepLCD.sizePolicy().hasHeightForWidth())
        self.stepLCD.setSizePolicy(sizePolicy)
        self.stepLCD.setObjectName("stepLCD")
        self.hboxlayout.addWidget(self.stepLCD)

        self.Run_Layout = QtGui.QWidget(MainPanel)
        self.Run_Layout.setGeometry(QtCore.QRect(11,442,538,32))
        self.Run_Layout.setObjectName("Run_Layout")

        self.hboxlayout1 = QtGui.QHBoxLayout(self.Run_Layout)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.buttonHelp = QtGui.QPushButton(self.Run_Layout)
        self.buttonHelp.setAutoDefault(True)
        self.buttonHelp.setObjectName("buttonHelp")
        self.hboxlayout1.addWidget(self.buttonHelp)

        spacerItem = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)

        self.buttonRun = QtGui.QPushButton(self.Run_Layout)
        self.buttonRun.setAutoDefault(True)
        self.buttonRun.setDefault(True)
        self.buttonRun.setObjectName("buttonRun")
        self.hboxlayout1.addWidget(self.buttonRun)

        self.buttonExit = QtGui.QPushButton(self.Run_Layout)
        self.buttonExit.setAutoDefault(True)
        self.buttonExit.setObjectName("buttonExit")
        self.hboxlayout1.addWidget(self.buttonExit)

        self.tabWidget = QtGui.QTabWidget(MainPanel)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setGeometry(QtCore.QRect(11,6,538,407))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName("tabWidget")

        self.Widget8 = QtGui.QWidget()
        self.Widget8.setObjectName("Widget8")

        self.splitter6 = QtGui.QSplitter(self.Widget8)
        self.splitter6.setGeometry(QtCore.QRect(10,0,520,360))
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

        self.layout7 = QtGui.QWidget(self.modSpec)
        self.layout7.setGeometry(QtCore.QRect(10,20,500,60))
        self.layout7.setObjectName("layout7")

        self.gridlayout = QtGui.QGridLayout(self.layout7)
        self.gridlayout.setObjectName("gridlayout")

        self.chooseButton = QtGui.QPushButton(self.layout7)
        self.chooseButton.setObjectName("chooseButton")
        self.gridlayout.addWidget(self.chooseButton,1,2,1,1)

        self.textLabel1 = QtGui.QLabel(self.layout7)
        self.textLabel1.setWordWrap(False)
        self.textLabel1.setObjectName("textLabel1")
        self.gridlayout.addWidget(self.textLabel1,0,0,1,1)

        spacerItem1 = QtGui.QSpacerItem(370,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1,0,1,1,3)

        self.scriptNameEdit = QtGui.QLineEdit(self.layout7)
        self.scriptNameEdit.setObjectName("scriptNameEdit")
        self.gridlayout.addWidget(self.scriptNameEdit,1,0,1,2)

        self.editButton = QtGui.QPushButton(self.layout7)
        self.editButton.setObjectName("editButton")
        self.gridlayout.addWidget(self.editButton,1,3,1,1)

        self.Database_layout = QtGui.QWidget(self.splitter6)
        self.Database_layout.setObjectName("Database_layout")

        self.gridlayout1 = QtGui.QGridLayout(self.Database_layout)
        self.gridlayout1.setObjectName("gridlayout1")

        spacerItem2 = QtGui.QSpacerItem(20,100,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem2,1,0,1,1)

        self.dbSpecGroupBox = QtGui.QGroupBox(self.Database_layout)
        self.dbSpecGroupBox.setEnabled(False)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dbSpecGroupBox.sizePolicy().hasHeightForWidth())
        self.dbSpecGroupBox.setSizePolicy(sizePolicy)
        self.dbSpecGroupBox.setObjectName("dbSpecGroupBox")

        self.layout71 = QtGui.QWidget(self.dbSpecGroupBox)
        self.layout71.setGeometry(QtCore.QRect(10,20,360,140))
        self.layout71.setObjectName("layout71")

        self.gridlayout2 = QtGui.QGridLayout(self.layout71)
        self.gridlayout2.setObjectName("gridlayout2")

        self.textLabel2 = QtGui.QLabel(self.layout71)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel2.sizePolicy().hasHeightForWidth())
        self.textLabel2.setSizePolicy(sizePolicy)
        self.textLabel2.setWordWrap(False)
        self.textLabel2.setObjectName("textLabel2")
        self.gridlayout2.addWidget(self.textLabel2,0,0,1,1)

        self.portEdit = QtGui.QLineEdit(self.layout71)
        self.portEdit.setObjectName("portEdit")
        self.gridlayout2.addWidget(self.portEdit,1,1,1,1)

        self.textLabel3 = QtGui.QLabel(self.layout71)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel3.sizePolicy().hasHeightForWidth())
        self.textLabel3.setSizePolicy(sizePolicy)
        self.textLabel3.setWordWrap(False)
        self.textLabel3.setObjectName("textLabel3")
        self.gridlayout2.addWidget(self.textLabel3,0,1,1,1)

        self.pwEdit = QtGui.QLineEdit(self.layout71)
        self.pwEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.pwEdit.setObjectName("pwEdit")
        self.gridlayout2.addWidget(self.pwEdit,3,1,1,1)

        self.textLabel1_2 = QtGui.QLabel(self.layout71)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel1_2.sizePolicy().hasHeightForWidth())
        self.textLabel1_2.setSizePolicy(sizePolicy)
        self.textLabel1_2.setWordWrap(False)
        self.textLabel1_2.setObjectName("textLabel1_2")
        self.gridlayout2.addWidget(self.textLabel1_2,2,1,1,1)

        self.textLabel4 = QtGui.QLabel(self.layout71)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel4.sizePolicy().hasHeightForWidth())
        self.textLabel4.setSizePolicy(sizePolicy)
        self.textLabel4.setWordWrap(False)
        self.textLabel4.setObjectName("textLabel4")
        self.gridlayout2.addWidget(self.textLabel4,2,0,1,1)

        self.hostnEdit = QtGui.QLineEdit(self.layout71)
        self.hostnEdit.setObjectName("hostnEdit")
        self.gridlayout2.addWidget(self.hostnEdit,1,0,1,1)

        self.uidEdit = QtGui.QLineEdit(self.layout71)
        self.uidEdit.setObjectName("uidEdit")
        self.gridlayout2.addWidget(self.uidEdit,3,0,1,1)
        self.gridlayout1.addWidget(self.dbSpecGroupBox,0,1,2,1)

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setObjectName("vboxlayout")

        self.textLabel1_11 = QtGui.QLabel(self.Database_layout)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel1_11.sizePolicy().hasHeightForWidth())
        self.textLabel1_11.setSizePolicy(sizePolicy)
        self.textLabel1_11.setWordWrap(False)
        self.textLabel1_11.setObjectName("textLabel1_11")
        self.vboxlayout.addWidget(self.textLabel1_11)

        self.dbType = QtGui.QComboBox(self.Database_layout)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dbType.sizePolicy().hasHeightForWidth())
        self.dbType.setSizePolicy(sizePolicy)
        self.dbType.setObjectName("dbType")
        self.vboxlayout.addWidget(self.dbType)
        self.gridlayout1.addLayout(self.vboxlayout,0,0,1,1)
        self.tabWidget.addTab(self.Widget8,"")

        self.Widget9 = QtGui.QWidget()
        self.Widget9.setObjectName("Widget9")

        self.layout9 = QtGui.QWidget(self.Widget9)
        self.layout9.setGeometry(QtCore.QRect(9,19,294,132))
        self.layout9.setObjectName("layout9")

        self.gridlayout3 = QtGui.QGridLayout(self.layout9)
        self.gridlayout3.setObjectName("gridlayout3")

        self.unameEdit = QtGui.QLineEdit(self.layout9)
        self.unameEdit.setObjectName("unameEdit")
        self.gridlayout3.addWidget(self.unameEdit,0,1,1,3)

        self.textLabel1_5 = QtGui.QLabel(self.layout9)
        self.textLabel1_5.setWordWrap(False)
        self.textLabel1_5.setObjectName("textLabel1_5")
        self.gridlayout3.addWidget(self.textLabel1_5,3,0,1,2)

        self.langCombo = QtGui.QComboBox(self.layout9)
        self.langCombo.setObjectName("langCombo")
        self.gridlayout3.addWidget(self.langCombo,3,2,1,2)

        self.textLabel5 = QtGui.QLabel(self.layout9)
        self.textLabel5.setWordWrap(False)
        self.textLabel5.setObjectName("textLabel5")
        self.gridlayout3.addWidget(self.textLabel5,1,0,1,1)

        self.textLabel2_3 = QtGui.QLabel(self.layout9)
        self.textLabel2_3.setWordWrap(False)
        self.textLabel2_3.setObjectName("textLabel2_3")
        self.gridlayout3.addWidget(self.textLabel2_3,2,0,1,3)

        self.textLabel2_2 = QtGui.QLabel(self.layout9)
        self.textLabel2_2.setWordWrap(False)
        self.textLabel2_2.setObjectName("textLabel2_2")
        self.gridlayout3.addWidget(self.textLabel2_2,0,0,1,1)

        self.editorEdit = QtGui.QLineEdit(self.layout9)
        self.editorEdit.setObjectName("editorEdit")
        self.gridlayout3.addWidget(self.editorEdit,1,1,1,3)

        self.pdfEdit = QtGui.QLineEdit(self.layout9)
        self.pdfEdit.setObjectName("pdfEdit")
        self.gridlayout3.addWidget(self.pdfEdit,2,3,1,1)
        self.tabWidget.addTab(self.Widget9,"")

        self.TabPage = QtGui.QWidget()
        self.TabPage.setObjectName("TabPage")

        self.line1 = QtGui.QFrame(self.TabPage)
        self.line1.setGeometry(QtCore.QRect(289,34,20,320))
        self.line1.setFrameShape(QtGui.QFrame.VLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.line1.setLineWidth(3)
        self.line1.setObjectName("line1")

        self.layout14 = QtGui.QWidget(self.TabPage)
        self.layout14.setGeometry(QtCore.QRect(0,10,280,350))
        self.layout14.setObjectName("layout14")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.layout14)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.textLabel5_2 = QtGui.QLabel(self.layout14)
        self.textLabel5_2.setWordWrap(False)
        self.textLabel5_2.setObjectName("textLabel5_2")
        self.vboxlayout1.addWidget(self.textLabel5_2)

        self.textEdit1 = QtGui.QTextEdit(self.layout14)
        self.textEdit1.setObjectName("textEdit1")
        self.vboxlayout1.addWidget(self.textEdit1)

        self.layout18 = QtGui.QWidget(self.TabPage)
        self.layout18.setGeometry(QtCore.QRect(320,10,200,349))
        self.layout18.setObjectName("layout18")

        self.vboxlayout2 = QtGui.QVBoxLayout(self.layout18)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.vboxlayout3 = QtGui.QVBoxLayout()
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.vboxlayout4 = QtGui.QVBoxLayout()
        self.vboxlayout4.setObjectName("vboxlayout4")

        self.textLabel1_3 = QtGui.QLabel(self.layout18)
        self.textLabel1_3.setAlignment(QtCore.Qt.AlignCenter)
        self.textLabel1_3.setWordWrap(False)
        self.textLabel1_3.setObjectName("textLabel1_3")
        self.vboxlayout4.addWidget(self.textLabel1_3)

        self.dbBackup = QtGui.QPushButton(self.layout18)
        self.dbBackup.setEnabled(False)
        self.dbBackup.setObjectName("dbBackup")
        self.vboxlayout4.addWidget(self.dbBackup)

        self.dbInfo = QtGui.QPushButton(self.layout18)
        self.dbInfo.setEnabled(False)
        self.dbInfo.setObjectName("dbInfo")
        self.vboxlayout4.addWidget(self.dbInfo)
        self.vboxlayout3.addLayout(self.vboxlayout4)

        self.line2 = QtGui.QFrame(self.layout18)
        self.line2.setFrameShape(QtGui.QFrame.HLine)
        self.line2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line2.setLineWidth(2)
        self.line2.setObjectName("line2")
        self.vboxlayout3.addWidget(self.line2)

        self.vboxlayout5 = QtGui.QVBoxLayout()
        self.vboxlayout5.setObjectName("vboxlayout5")

        self.textLabel1_4 = QtGui.QLabel(self.layout18)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel1_4.sizePolicy().hasHeightForWidth())
        self.textLabel1_4.setSizePolicy(sizePolicy)
        self.textLabel1_4.setAlignment(QtCore.Qt.AlignCenter)
        self.textLabel1_4.setWordWrap(False)
        self.textLabel1_4.setMargin(0)
        self.textLabel1_4.setObjectName("textLabel1_4")
        self.vboxlayout5.addWidget(self.textLabel1_4)

        self.repOpen = QtGui.QPushButton(self.layout18)
        self.repOpen.setObjectName("repOpen")
        self.vboxlayout5.addWidget(self.repOpen)
        self.vboxlayout3.addLayout(self.vboxlayout5)
        self.vboxlayout2.addLayout(self.vboxlayout3)

        spacerItem3 = QtGui.QSpacerItem(20,170,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout2.addItem(spacerItem3)
        self.tabWidget.addTab(self.TabPage,"")

        self.visPage = QtGui.QWidget()
        self.visPage.setObjectName("visPage")

        self.layout24 = QtGui.QWidget(self.visPage)
        self.layout24.setGeometry(QtCore.QRect(0,279,530,71))
        self.layout24.setObjectName("layout24")

        self.hboxlayout2 = QtGui.QHBoxLayout(self.layout24)
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.vboxlayout6 = QtGui.QVBoxLayout()
        self.vboxlayout6.setObjectName("vboxlayout6")

        self.textLabel1_9 = QtGui.QLabel(self.layout24)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel1_9.sizePolicy().hasHeightForWidth())
        self.textLabel1_9.setSizePolicy(sizePolicy)
        self.textLabel1_9.setWordWrap(False)
        self.textLabel1_9.setObjectName("textLabel1_9")
        self.vboxlayout6.addWidget(self.textLabel1_9)

        self.consensusButton = QtGui.QPushButton(self.layout24)
        self.consensusButton.setEnabled(False)
        self.consensusButton.setObjectName("consensusButton")
        self.vboxlayout6.addWidget(self.consensusButton)
        self.hboxlayout2.addLayout(self.vboxlayout6)

        spacerItem4 = QtGui.QSpacerItem(260,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem4)

        self.layout20 = QtGui.QWidget(self.visPage)
        self.layout20.setGeometry(QtCore.QRect(0,10,265,263))
        self.layout20.setObjectName("layout20")

        self.vboxlayout7 = QtGui.QVBoxLayout(self.layout20)
        self.vboxlayout7.setObjectName("vboxlayout7")

        self.textLabel1_7 = QtGui.QLabel(self.layout20)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel1_7.sizePolicy().hasHeightForWidth())
        self.textLabel1_7.setSizePolicy(sizePolicy)
        self.textLabel1_7.setWordWrap(False)
        self.textLabel1_7.setObjectName("textLabel1_7")
        self.vboxlayout7.addWidget(self.textLabel1_7)

        self.tableList = QtGui.QComboBox(self.layout20)
        self.tableList.setObjectName("tableList")
        self.vboxlayout7.addWidget(self.tableList)

        self.textLabel1_10 = QtGui.QLabel(self.layout20)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel1_10.sizePolicy().hasHeightForWidth())
        self.textLabel1_10.setSizePolicy(sizePolicy)
        self.textLabel1_10.setWordWrap(False)
        self.textLabel1_10.setObjectName("textLabel1_10")
        self.vboxlayout7.addWidget(self.textLabel1_10)

        self.variableList = QtGui.QComboBox(self.layout20)
        self.variableList.setObjectName("variableList")
        self.vboxlayout7.addWidget(self.variableList)

        self.textLabel2_4 = QtGui.QLabel(self.layout20)
        self.textLabel2_4.setEnabled(True)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel2_4.sizePolicy().hasHeightForWidth())
        self.textLabel2_4.setSizePolicy(sizePolicy)
        self.textLabel2_4.setWordWrap(False)
        self.textLabel2_4.setObjectName("textLabel2_4")
        self.vboxlayout7.addWidget(self.textLabel2_4)

        self.mapList = QtGui.QComboBox(self.layout20)
        self.mapList.setEnabled(True)
        self.mapList.setObjectName("mapList")
        self.vboxlayout7.addWidget(self.mapList)

        self.layout19 = QtGui.QWidget(self.visPage)
        self.layout19.setGeometry(QtCore.QRect(272,11,260,261))
        self.layout19.setObjectName("layout19")

        self.vboxlayout8 = QtGui.QVBoxLayout(self.layout19)
        self.vboxlayout8.setObjectName("vboxlayout8")

        self.dbscanButton = QtGui.QPushButton(self.layout19)
        self.dbscanButton.setObjectName("dbscanButton")
        self.vboxlayout8.addWidget(self.dbscanButton)

        self.textLabel1_8 = QtGui.QLabel(self.layout19)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textLabel1_8.sizePolicy().hasHeightForWidth())
        self.textLabel1_8.setSizePolicy(sizePolicy)
        self.textLabel1_8.setWordWrap(False)
        self.textLabel1_8.setObjectName("textLabel1_8")
        self.vboxlayout8.addWidget(self.textLabel1_8)

        self.rateSpinBox = QtGui.QSpinBox(self.layout19)
        self.rateSpinBox.setMinimum(20)
        self.rateSpinBox.setObjectName("rateSpinBox")
        self.vboxlayout8.addWidget(self.rateSpinBox)

        spacerItem5 = QtGui.QSpacerItem(20,90,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout8.addItem(spacerItem5)

        self.playButton_2D = QtGui.QPushButton(self.layout19)
        self.playButton_2D.setEnabled(False)
        self.playButton_2D.setObjectName("playButton_2D")
        self.vboxlayout8.addWidget(self.playButton_2D)

        self.playButton = QtGui.QPushButton(self.layout19)
        self.playButton.setObjectName("playButton")
        self.vboxlayout8.addWidget(self.playButton)
        self.tabWidget.addTab(self.visPage,"")

        self.retranslateUi(MainPanel)
        self.dbType.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainPanel)

    def retranslateUi(self, MainPanel):
        MainPanel.setWindowTitle(QtGui.QApplication.translate("MainPanel", "Epigrass Control Panel", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_6.setText(QtGui.QApplication.translate("MainPanel", "Progress:", None, QtGui.QApplication.UnicodeUTF8))
        self.stepLCD.setToolTip(QtGui.QApplication.translate("MainPanel", "Simulation step", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonHelp.setToolTip(QtGui.QApplication.translate("MainPanel", "Click here to open the userguide in the web browser", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonHelp.setText(QtGui.QApplication.translate("MainPanel", "&Help", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonHelp.setShortcut(QtGui.QApplication.translate("MainPanel", "F1", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonRun.setToolTip(QtGui.QApplication.translate("MainPanel", "Click here to start your simulation", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonRun.setText(QtGui.QApplication.translate("MainPanel", "&Run", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonRun.setShortcut(QtGui.QApplication.translate("MainPanel", "Alt+R", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonExit.setToolTip(QtGui.QApplication.translate("MainPanel", "Click here to leave Epigrass", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonExit.setText(QtGui.QApplication.translate("MainPanel", "&Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonExit.setShortcut(QtGui.QApplication.translate("MainPanel", "Alt+E", None, QtGui.QApplication.UnicodeUTF8))
        self.modSpec.setTitle(QtGui.QApplication.translate("MainPanel", "Model Specification", None, QtGui.QApplication.UnicodeUTF8))
        self.chooseButton.setText(QtGui.QApplication.translate("MainPanel", "Choose", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1.setText(QtGui.QApplication.translate("MainPanel", "Script Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.scriptNameEdit.setToolTip(QtGui.QApplication.translate("MainPanel", "write the name of the your script or press the choose button on the right to select one.", None, QtGui.QApplication.UnicodeUTF8))
        self.editButton.setText(QtGui.QApplication.translate("MainPanel", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.dbSpecGroupBox.setTitle(QtGui.QApplication.translate("MainPanel", "Database Specification", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2.setText(QtGui.QApplication.translate("MainPanel", "Host:", None, QtGui.QApplication.UnicodeUTF8))
        self.portEdit.setToolTip(QtGui.QApplication.translate("MainPanel", "Enter the port  the server listens to.", None, QtGui.QApplication.UnicodeUTF8))
        self.portEdit.setText(QtGui.QApplication.translate("MainPanel", "3306", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel3.setText(QtGui.QApplication.translate("MainPanel", "Port:", None, QtGui.QApplication.UnicodeUTF8))
        self.pwEdit.setToolTip(QtGui.QApplication.translate("MainPanel", "Database password for the userid entered", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2.setText(QtGui.QApplication.translate("MainPanel", "Password:", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel4.setText(QtGui.QApplication.translate("MainPanel", "Userid:", None, QtGui.QApplication.UnicodeUTF8))
        self.hostnEdit.setToolTip(QtGui.QApplication.translate("MainPanel", "This is the url of your database server.", None, QtGui.QApplication.UnicodeUTF8))
        self.hostnEdit.setText(QtGui.QApplication.translate("MainPanel", "localhost", None, QtGui.QApplication.UnicodeUTF8))
        self.uidEdit.setToolTip(QtGui.QApplication.translate("MainPanel", "This is the userid for accessing the database server", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_11.setText(QtGui.QApplication.translate("MainPanel", "Database type:", None, QtGui.QApplication.UnicodeUTF8))
        self.dbType.setToolTip(QtGui.QApplication.translate("MainPanel", "Select your database type", None, QtGui.QApplication.UnicodeUTF8))
        self.dbType.addItem(QtGui.QApplication.translate("MainPanel", "MySQL", None, QtGui.QApplication.UnicodeUTF8))
        self.dbType.addItem(QtGui.QApplication.translate("MainPanel", "SQLite", None, QtGui.QApplication.UnicodeUTF8))
        self.dbType.addItem(QtGui.QApplication.translate("MainPanel", "CSV", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Widget8), QtGui.QApplication.translate("MainPanel", "Run Options", None, QtGui.QApplication.UnicodeUTF8))
        self.unameEdit.setToolTip(QtGui.QApplication.translate("MainPanel", "Enter your full name. This will be added to the report.", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_5.setText(QtGui.QApplication.translate("MainPanel", "Language", None, QtGui.QApplication.UnicodeUTF8))
        self.langCombo.setToolTip(QtGui.QApplication.translate("MainPanel", "Select the language for the GUI", None, QtGui.QApplication.UnicodeUTF8))
        self.langCombo.addItem(QtGui.QApplication.translate("MainPanel", "English", None, QtGui.QApplication.UnicodeUTF8))
        self.langCombo.addItem(QtGui.QApplication.translate("MainPanel", "Brazilian portuguese", None, QtGui.QApplication.UnicodeUTF8))
        self.langCombo.addItem(QtGui.QApplication.translate("MainPanel", "French", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel5.setText(QtGui.QApplication.translate("MainPanel", "Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2_3.setText(QtGui.QApplication.translate("MainPanel", "PDF Viewer", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2_2.setText(QtGui.QApplication.translate("MainPanel", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.editorEdit.setToolTip(QtGui.QApplication.translate("MainPanel", "Enter your preferred text editor", None, QtGui.QApplication.UnicodeUTF8))
        self.pdfEdit.setToolTip(QtGui.QApplication.translate("MainPanel", "Enter the name of your preferred PDF viewer", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Widget9), QtGui.QApplication.translate("MainPanel", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel5_2.setText(QtGui.QApplication.translate("MainPanel", "Simulation Status", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_3.setText(QtGui.QApplication.translate("MainPanel", "Database", None, QtGui.QApplication.UnicodeUTF8))
        self.dbBackup.setToolTip(QtGui.QApplication.translate("MainPanel", "Click here to backup the epigrass database ", None, QtGui.QApplication.UnicodeUTF8))
        self.dbBackup.setText(QtGui.QApplication.translate("MainPanel", "Backup", None, QtGui.QApplication.UnicodeUTF8))
        self.dbInfo.setToolTip(QtGui.QApplication.translate("MainPanel", "Click here for a short description of the epigrass database", None, QtGui.QApplication.UnicodeUTF8))
        self.dbInfo.setText(QtGui.QApplication.translate("MainPanel", "Info", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_4.setText(QtGui.QApplication.translate("MainPanel", "Report", None, QtGui.QApplication.UnicodeUTF8))
        self.repOpen.setText(QtGui.QApplication.translate("MainPanel", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.TabPage), QtGui.QApplication.translate("MainPanel", "Utilities", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_9.setText(QtGui.QApplication.translate("MainPanel", "Spread Trees", None, QtGui.QApplication.UnicodeUTF8))
        self.consensusButton.setToolTip(QtGui.QApplication.translate("MainPanel", "Select a directory with tree-files to build consensus on.", None, QtGui.QApplication.UnicodeUTF8))
        self.consensusButton.setText(QtGui.QApplication.translate("MainPanel", "Consensus Tree", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_7.setText(QtGui.QApplication.translate("MainPanel", "Simulations stored:", None, QtGui.QApplication.UnicodeUTF8))
        self.tableList.setToolTip(QtGui.QApplication.translate("MainPanel", "Select a database stored simulation", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_10.setText(QtGui.QApplication.translate("MainPanel", "Variable to display:", None, QtGui.QApplication.UnicodeUTF8))
        self.variableList.setToolTip(QtGui.QApplication.translate("MainPanel", "Select a variable to display in the animation", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2_4.setText(QtGui.QApplication.translate("MainPanel", "Maps available:", None, QtGui.QApplication.UnicodeUTF8))
        self.mapList.setToolTip(QtGui.QApplication.translate("MainPanel", "Select a map", None, QtGui.QApplication.UnicodeUTF8))
        self.mapList.addItem(QtGui.QApplication.translate("MainPanel", "No map", None, QtGui.QApplication.UnicodeUTF8))
        self.dbscanButton.setText(QtGui.QApplication.translate("MainPanel", "Scan DB", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_8.setText(QtGui.QApplication.translate("MainPanel", "Animation rate", None, QtGui.QApplication.UnicodeUTF8))
        self.playButton_2D.setText(QtGui.QApplication.translate("MainPanel", "Start 2D animation", None, QtGui.QApplication.UnicodeUTF8))
        self.playButton.setText(QtGui.QApplication.translate("MainPanel", "Start 3D animation", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.visPage), QtGui.QApplication.translate("MainPanel", "Visualization", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainPanel = QtGui.QWidget()
    ui = Ui_MainPanel()
    ui.setupUi(MainPanel)
    MainPanel.show()
    sys.exit(app.exec_())
