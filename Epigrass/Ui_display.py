# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/fccoelho/Documents/Projects_software/epigrass/epigrassqt4/display.ui'
#
# Created: Sun May  4 20:11:54 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,778,739).size()).expandedTo(Form.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)

        self.widget = QtGui.QWidget(Form)
        self.widget.setGeometry(QtCore.QRect(10,2,761,731))
        self.widget.setObjectName("widget")

        self.vboxlayout = QtGui.QVBoxLayout(self.widget)
        self.vboxlayout.setObjectName("vboxlayout")

        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName("label")
        self.vboxlayout.addWidget(self.label)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")

        self.splitter = QtGui.QSplitter(self.widget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")

        self.mapView = QtGui.QGraphicsView(self.splitter)
        self.mapView.setProperty("cursor",QtCore.QVariant(QtCore.Qt.PointingHandCursor))
        self.mapView.setAutoFillBackground(True)
        self.mapView.setObjectName("mapView")

        self.layoutWidget = QtGui.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.layoutWidget)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.horizontalSlider = QtGui.QSlider(self.layoutWidget)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.vboxlayout1.addWidget(self.horizontalSlider)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.label_2 = QtGui.QLabel(self.layoutWidget)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.hboxlayout1.addWidget(self.label_2)

        spacerItem = QtGui.QSpacerItem(461,23,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)

        self.lcdNumber = QtGui.QLCDNumber(self.layoutWidget)
        self.lcdNumber.setObjectName("lcdNumber")
        self.hboxlayout1.addWidget(self.lcdNumber)
        self.vboxlayout1.addLayout(self.hboxlayout1)

        self.qwtPlot = QwtPlot(self.layoutWidget)
        self.qwtPlot.setObjectName("qwtPlot")
        self.vboxlayout1.addWidget(self.qwtPlot)
        self.hboxlayout.addWidget(self.splitter)

        self.vboxlayout2 = QtGui.QVBoxLayout()
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.pushButton = QtGui.QPushButton(self.widget)
        self.pushButton.setObjectName("pushButton")
        self.vboxlayout2.addWidget(self.pushButton)

        self.pushButton_2 = QtGui.QPushButton(self.widget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.vboxlayout2.addWidget(self.pushButton_2)

        spacerItem1 = QtGui.QSpacerItem(20,521,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout2.addItem(spacerItem1)
        self.hboxlayout.addLayout(self.vboxlayout2)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Simulation Display", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Geographical View", None, QtGui.QApplication.UnicodeUTF8))
        self.mapView.setToolTip(QtGui.QApplication.translate("Form", "Select a polygon to see its local time series.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Time Series", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Form", "Play", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("Form", "Stop", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4.Qwt5 import QwtPlot


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
