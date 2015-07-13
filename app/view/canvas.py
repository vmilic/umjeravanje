# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 12:27:25 2015

@author: DHMZ-Milic

"""
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigCanvas
from matplotlib.figure import Figure


class Kanvas(FigCanvas):
    """
    Canvas za prikaz grafova
    init sa dictom lebela za osi
    """
    def __init__(self, meta=None, parent=None, width=3, height=3, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        FigCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigCanvas.setSizePolicy(self,
                                QtGui.QSizePolicy.MinimumExpanding,
                                QtGui.QSizePolicy.MinimumExpanding)
        FigCanvas.updateGeometry(self)
        self.meta = meta
        self.setup_labels()
        self.fig.set_tight_layout(True)

    def setup_labels(self):
        """
        Try to set labels to graph
        """
        try:
            self.axes.set_xlabel(self.meta['xlabel'], fontsize=8)
            self.axes.set_ylabel(self.meta['ylabel'], fontsize=8)
            self.axes.set_title(self.meta['title'], fontsize=10)
        except (KeyError, ValueError, TypeError):
            pass

    def clear_graf(self):
        """
        clear graf & redo labels
        """
        self.axes.clear()
        self.setup_labels()

    def crtaj(self, x, y):
        """
        Naredba za plot, trazi listu x, y tocaka.
        """
        self.clear_graf()
        self.axes.scatter(x,
                          y,
                          marker='o',
                          s=10,
                          color='b',
                          alpha=0.5)
        minimum = min(x)
        maksimum = max(x)
        delta = (maksimum - minimum) / 20
        minimum = minimum - delta
        maksimum = maksimum + delta
        # TODO! extend granica grafa za neki x....
        self.axes.set_xlim((minimum, maksimum))
        self.draw()
