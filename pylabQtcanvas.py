#! /usr/bin/env python

# embedding_in_qt.py --- Simple Qt application embedding matplotlib canvases
#
# Copyright (C) 2005 Florent Rougon
#
# This file is an example program for matplotlib. It may be used and
# modified with no restriction; raw copies as well as modified versions
# may be distributed without limitation.

import sys, os, random
from qt import *

from matplotlib.numerix import arange, sin, pi
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pylab import plot

# This seems to be what PyQt expects, according to the examples shipped in
# its distribution.
TRUE  = 1
FALSE = 0

progname = os.path.basename(sys.argv[0])
progversion = "0.1"

# Note: color-intensive applications may require a different color allocation
# strategy.
#QApplication.setColorSpec(QApplication.NormalColor)
#app = QApplication(sys.argv)

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)
        self.plot = plot

        #self.compute_initial_figure()

        FigureCanvas.__init__(self, self.fig)
        self.reparent(parent, QPoint(0, 0))

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def sizeHint(self):
        w, h = self.get_width_height()
        return QSize(w, h)

    def minimumSizeHint(self):
        return QSize(10, 10)


