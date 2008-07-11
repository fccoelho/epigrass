# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/flavio/Documents/Projetos/Epigrass/Epigrass-devel-qt4/epgeditor.ui'
#
# Created: Fri Jul 11 17:40:29 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(QtCore.QSize(QtCore.QRect(0,0,505,732).size()).expandedTo(MainWindow.minimumSizeHint()))
        MainWindow.setWindowIcon(QtGui.QIcon(":/egicon.png"))

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setGeometry(QtCore.QRect(0,31,505,673))
        self.centralwidget.setObjectName("centralwidget")

        self.vboxlayout = QtGui.QVBoxLayout(self.centralwidget)
        self.vboxlayout.setObjectName("vboxlayout")

        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")

        self.tab = QtGui.QWidget()
        self.tab.setGeometry(QtCore.QRect(0,0,485,621))
        self.tab.setObjectName("tab")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.tab)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.treeWidget = QtGui.QTreeWidget(self.tab)
        self.treeWidget.setMouseTracking(True)
        self.treeWidget.setAlternatingRowColors(True)
        self.treeWidget.setSortingEnabled(True)
        self.treeWidget.setAnimated(True)
        self.treeWidget.setWordWrap(True)
        self.treeWidget.setColumnCount(3)
        self.treeWidget.setObjectName("treeWidget")
        self.vboxlayout1.addWidget(self.treeWidget)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")

        self.addVButton = QtGui.QPushButton(self.tab)
        self.addVButton.setObjectName("addVButton")
        self.hboxlayout.addWidget(self.addVButton)

        self.exitButton = QtGui.QPushButton(self.tab)
        self.exitButton.setObjectName("exitButton")
        self.hboxlayout.addWidget(self.exitButton)
        self.vboxlayout1.addLayout(self.hboxlayout)
        self.tabWidget.addTab(self.tab,"")

        self.tab_2 = QtGui.QWidget()
        self.tab_2.setGeometry(QtCore.QRect(0,0,485,621))
        self.tab_2.setObjectName("tab_2")

        self.vboxlayout2 = QtGui.QVBoxLayout(self.tab_2)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.epgView = QtGui.QTextBrowser(self.tab_2)
        self.epgView.setObjectName("epgView")
        self.vboxlayout2.addWidget(self.epgView)
        self.tabWidget.addTab(self.tab_2,"")

        self.help_tab = QtGui.QWidget()
        self.help_tab.setGeometry(QtCore.QRect(0,0,485,621))
        self.help_tab.setObjectName("help_tab")

        self.vboxlayout3 = QtGui.QVBoxLayout(self.help_tab)
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.helpBrowser = QtGui.QTextBrowser(self.help_tab)
#        self.helpBrowser.setSource(QtCore.QUrl("file:///"))
        self.helpBrowser.setObjectName("helpBrowser")
        self.vboxlayout3.addWidget(self.helpBrowser)
        self.tabWidget.addTab(self.help_tab,"")
        self.vboxlayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,505,31))
        self.menubar.setObjectName("menubar")

        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")

        self.menu_Help = QtGui.QMenu(self.menubar)
        self.menu_Help.setObjectName("menu_Help")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setGeometry(QtCore.QRect(0,704,505,28))
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.action_Help = QtGui.QAction(MainWindow)
        self.action_Help.setObjectName("action_Help")

        self.action_About = QtGui.QAction(MainWindow)
        self.action_About.setObjectName("action_About")

        self.actionAbout_Epigrass = QtGui.QAction(MainWindow)
        self.actionAbout_Epigrass.setObjectName("actionAbout_Epigrass")

        self.actionAuto_Refresh = QtGui.QAction(MainWindow)
        self.actionAuto_Refresh.setCheckable(True)
        self.actionAuto_Refresh.setObjectName("actionAuto_Refresh")

        self.action_Open_epg_File = QtGui.QAction(MainWindow)
        self.action_Open_epg_File.setObjectName("action_Open_epg_File")

        self.action_Save = QtGui.QAction(MainWindow)
        self.action_Save.setObjectName("action_Save")

        self.actionE_xit = QtGui.QAction(MainWindow)
        self.actionE_xit.setObjectName("actionE_xit")

        self.action_Refresh = QtGui.QAction(MainWindow)
        self.action_Refresh.setObjectName("action_Refresh")

        self.action_New = QtGui.QAction(MainWindow)
        self.action_New.setObjectName("action_New")
        self.menuFile.addAction(self.action_New)
        self.menuFile.addAction(self.action_Open_epg_File)
        self.menuFile.addAction(self.action_Save)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionE_xit)
        self.menu_Help.addAction(self.action_Help)
        self.menu_Help.addAction(self.action_About)
        self.menu_Help.addSeparator()
        self.menu_Help.addAction(self.actionAbout_Epigrass)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", ".EPG Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(0,QtGui.QApplication.translate("MainWindow", "Variable", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(1,QtGui.QApplication.translate("MainWindow", "Value", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(2,QtGui.QApplication.translate("MainWindow", "Description", None, QtGui.QApplication.UnicodeUTF8))
        self.addVButton.setToolTip(QtGui.QApplication.translate("MainWindow", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Save file</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.addVButton.setText(QtGui.QApplication.translate("MainWindow", "Add variable", None, QtGui.QApplication.UnicodeUTF8))
        self.exitButton.setToolTip(QtGui.QApplication.translate("MainWindow", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Leave the editor.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.exitButton.setText(QtGui.QApplication.translate("MainWindow", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("MainWindow", "Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("MainWindow", "Viewer", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.help_tab), QtGui.QApplication.translate("MainWindow", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.help_tab),QtGui.QApplication.translate("MainWindow", "Usage help", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Help.setTitle(QtGui.QApplication.translate("MainWindow", "&Help", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Help.setText(QtGui.QApplication.translate("MainWindow", "&Help", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Help.setShortcut(QtGui.QApplication.translate("MainWindow", "F1", None, QtGui.QApplication.UnicodeUTF8))
        self.action_About.setText(QtGui.QApplication.translate("MainWindow", "&About", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout_Epigrass.setText(QtGui.QApplication.translate("MainWindow", "About &Epigrass", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAuto_Refresh.setText(QtGui.QApplication.translate("MainWindow", "Auto-&Refresh", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Open_epg_File.setText(QtGui.QApplication.translate("MainWindow", "&Open .epg File", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Open_epg_File.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+O", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Save.setText(QtGui.QApplication.translate("MainWindow", "&Save", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Save.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+S", None, QtGui.QApplication.UnicodeUTF8))
        self.actionE_xit.setText(QtGui.QApplication.translate("MainWindow", "E&xit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionE_xit.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+X", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Refresh.setText(QtGui.QApplication.translate("MainWindow", "&Refresh", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Refresh.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+R", None, QtGui.QApplication.UnicodeUTF8))
        self.action_New.setText(QtGui.QApplication.translate("MainWindow", "&New", None, QtGui.QApplication.UnicodeUTF8))
        self.action_New.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+N", None, QtGui.QApplication.UnicodeUTF8))

import epigrass_rc


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
