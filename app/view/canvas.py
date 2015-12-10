# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 12:27:25 2015

@author: DHMZ-Milic

"""
import numpy as np
import pandas as pd
import datetime
import logging
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
                                QtGui.QSizePolicy.Fixed)

        FigCanvas.updateGeometry(self)
        self.meta = meta
        self.setup_labels()
        self.fig.set_tight_layout(True)

    def set_slope_offset(self, s, o):
        """setter za slope i offset ako je provjera linearnosti ON"""
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
            #korelacija i slope/offset labeli
            korelacija = np.corrcoef(x, y)[0][1]
            if b > 0:
                tekstl1 = 'pravac: c={0}*cref+{1}'.format(str(round(a, 2)), str(round(b, 2)))
            elif b < 0:
                tekstl1 = 'pravac: c={0}*cref{1}'.format(str(round(a, 2)), str(round(b, 2)))
            else:
                tekstl1 = 'pravac: c={0}*cref'.format(str(round(a, 2)))
            tekstl2 = 'korelacija = {0}'.format(str(round(korelacija, 4)))
            tekst = "\n".join([tekstl1, tekstl2])
            self.axes.text(0.8,
                           0.2,
                           tekst,
                           horizontalalignment='center',
                           verticalalignment='center',
                           fontsize=8,
                           transform = self.axes.transAxes,
                           bbox=dict(facecolor='blue', alpha=0.2))
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
            if x != [] and y != []:
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
        if minlist != [] and maxlist != []:
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

class GrafPreuzetihPodataka(FigCanvas):
    """kanvas za graficki prikaz preuzetih podataka"""
    def __init__(self, meta=None, parent=None, width=9, height=5, dpi=100):
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
        #dodatni niz random boja za graf
        self.randomBoje = [
            (0.09, 0.58, 0.58),
            (0.09, 0.09, 0.58),
            (0.09, 0.58, 0.09),
            (0.58, 0.09, 0.09)]
        rc = [tuple(np.random.random(size=3)) for i in range(10)]
        for i in rc:
            self.randomBoje.append(i)

    def setup_labels(self):
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

    def reset_graf(self):
        self.clear_graf()
        self.draw()

    def crtaj(self, frejm=None, raspon=None):
        """
        metoda za crtanje podataka na graf
        frejm --> pandas datafrejm sa podacima
        raspon --> integer broj minuta za prikaz na grafu
        """
        self.clear_graf()
        zadnji = frejm.index[-1] #zadnji indeks
        prvi = zadnji - datetime.timedelta(minutes=raspon) #prvi indeks
        if frejm.index[0] > prvi:
            prozor = frejm
            shift = False
        else:
            prozor = frejm[(frejm.index >= prvi) & (frejm.index <= zadnji)]
            shift = True

        vrijeme = list(prozor.index)
        for column in prozor.columns:
            y = prozor.loc[:, column]
            i = list(prozor.columns).index(column)
            boja = self.randomBoje[i]
            #plot
            txt=" ".join(['Plin',str(column)])
            self.axes.plot(vrijeme,
                           y,
                           linewidth=1,
                           color=boja,
                           alpha=0.5,
                           label=txt)
        if shift:
            minimum = max(vrijeme) - datetime.timedelta(minutes=raspon)
            maksimum = max(vrijeme)
        else:
            minimum = min(vrijeme)
            maksimum = min(vrijeme) + datetime.timedelta(minutes=raspon)
        delta = (maksimum - minimum) / 20
        minimum = minimum - delta
        maksimum = maksimum + delta
        self.axes.set_xlim((minimum, maksimum))
        allXLabels = self.axes.get_xticklabels(which='both') #dohvati sve labele
        for label in allXLabels:
            label.set_rotation(20)
            label.set_fontsize(8)

        self.legenda = self.axes.legend(loc=1,
                                        fontsize=8,
                                        fancybox=True)
        self.draw()


class RiseFallKanvas(FigCanvas):
    """
    Canvas za prikaz grafova
    init sa dictom lebela za osi
    """
    def __init__(self, meta=None, parent=None, width=8, height=5, dpi=100):
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

    def crtaj(self, podaci=None, rezultati=None, high=90, low=10):
        """
        naredba za plot
        -podaci su frejm sirovih podataka
        -rezultati su frejm izabranih vremena upona i padova
        """
        self.clear_graf()
        #print podataka
        x = list(podaci.index)
        y = list(podaci[:])
        self.axes.plot(x,
                       y,
                       color='b',
                       linewidth=0.8)
        #set vertikalni raspon
        ymin = 0
        ymax = 10
        if len(y):
            ymin = min(y) #possible empty sequence on empty series..#TODO!
            ymax = max(y)
            delta = (ymax - ymin) / 20
            ymin = ymin - delta
            ymax = ymax + delta
        self.axes.set_ylim((ymin, ymax))
        #set horizontalni raspon
        minimum = 0
        maksimum = 10
        if len(x):
            minimum = min(x)
            maksimum = max(x)
            delta = (maksimum - minimum) / 100
            minimum = minimum - delta
            maksimum = maksimum + delta
        self.axes.set_xlim((minimum, maksimum))
        #label size & orientation
        allXLabels = self.axes.get_xticklabels(which='both')
        for label in allXLabels:
            label.set_rotation(20)
            label.set_fontsize(8)
        #print vertikalnih linija iz rezultata
        indeksi = rezultati.index
        if len(indeksi) != 0:
            for ind in indeksi:
                value = rezultati.loc[ind, 'Naziv']
                start = rezultati.loc[ind, 'Pocetak']
                kraj= rezultati.loc[ind, 'Kraj']
                delta = rezultati.loc[ind, 'Delta']
                if isinstance(kraj, pd.tslib.NaTType):
                    pass
                else:
                    if 'RISE' in value:
                        self.axes.vlines(start, ymin, ymax, linestyles='dotted', color='g')
                        self.axes.vlines(kraj, ymin, ymax, linestyles='dotted', color='g')
                        self.axes.axvspan(start, kraj, color='g', alpha=0.2)
                    elif 'FALL' in value:
                        self.axes.vlines(start, ymin, ymax, linestyles='dotted', color='r')
                        self.axes.vlines(kraj, ymin, ymax, linestyles='dotted', color='r')
                        self.axes.axvspan(start, kraj, color='r', alpha=0.2)
                    else:
                        pass
        # raspon za rise i fall
        self.axes.hlines(low, minimum, maksimum, linestyles='dashed', color='k', alpha=0.4)
        self.axes.hlines(high, minimum, maksimum, linestyles='dashed', color='k', alpha=0.4)
        #zavrsna naredba za crtanje
        self.draw()
