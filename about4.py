# -*- coding: utf-8 -*-

"""
Module implementing aboutDialog.
"""

from PyQt4.QtGui import QDialog
from PyQt4.QtCore import pyqtSignature

from Ui_about4 import Ui_aboutDialog

class aboutDialog(QDialog, Ui_aboutDialog):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
