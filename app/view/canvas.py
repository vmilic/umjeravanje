# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 12:27:25 2015

@author: DHMZ-Milic

"""
import numpy as np
import datetime
import logging
from PyQt4 import QtGui
import matplotlib
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
                                QtGui.QSizePolicy.Fixed)

        FigCanvas.updateGeometry(self)
        self.meta = meta
        self.setup_labels()
        self.fig.set_tight_layout(True)

    def set_slope_offset(self, s, o):
        """setter za slope i offsegt ako je provjera linearnosti ON"""
        self.slope = s
        self.offset = o

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
        self.axes.set_xlim((minimum, maksimum))
        allXLabels = self.axes.get_xticklabels(which='both') #dohvati sve labele
        for label in allXLabels:
            label.set_rotation(20)
            label.set_fontsize(8)
        try:
            a = float(self.slope)
            b = float(self.offset)
        except Exception as err:
            logging.error('problem sa slope i offset za crtanje pravca. '+str(err), exc_info=True)
            a = None
            b = None
        if a is not None and b is not None:
            xos = [minimum, maksimum]
            yos = [(a*minimum)+b, (a*maksimum)+b]
            self.axes.plot(xos,
                           yos,
                           'k-')
        self.draw()


class KanvasMjerenja(Kanvas):
    def __init__(self, meta=None, parent=None, width=3, height=3, dpi=100):
        Kanvas.__init__(self, meta=meta, parent=parent, width=width, height=height, dpi=dpi)

    def crtaj(self, frejm, tocke):
        """
        naredba za plot
        """
        self.clear_graf()
        minlist = []
        maxlist = []
        for tocka in tocke:
            x, y = self.get_tocke_za_crtanje(frejm, tocka)
            minlist.append(min(x))
            maxlist.append(max(x))
            r, g, b, a = tocka.boja.getRgb()
            boja = (r/255, g/255, b/255)
            alpha = a/255
            self.axes.scatter(x,
                              y,
                              marker='o',
                              s=10,
                              color=boja,
                              alpha=alpha)
        xmin, xmax = min(minlist), max(maxlist)
        delta = datetime.timedelta(minutes=10)
        xmin = xmin - delta
        xmax = xmax + delta
        self.axes.set_xlim((xmin, xmax))
        allXLabels = self.axes.get_xticklabels(which='both') #dohvati sve labele
        for label in allXLabels:
            label.set_rotation(20)
            label.set_fontsize(8)
        self.draw()

    def get_tocke_za_crtanje(self, frejm, tocka):
        """
        metoda za zadani frejm podataka i tocku vaca dvije liste (X kooridinate,
        Y kooridinate) sa podacima koje treba crtati
        """
        low = min(tocka.indeksi)
        high = max(tocka.indeksi)
        slajs = frejm.iloc[low:high+1]
        y = []
        x = []
        for i in range(0, len(slajs), 3):
            s = slajs[i:i+3]
            if len(s) == 3:
                valueX = slajs.index[i]
                valueY = np.average(s)
                x.append(valueX)
                y.append(valueY)
        return x, y
