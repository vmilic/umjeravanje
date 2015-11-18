# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 09:08:43 2015

@author: DHMZ-Milic
"""
import gc
import sys
import sip
import logging
import numpy as np
import pandas as pd
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigCanvas
from matplotlib.figure import Figure

################################################################################
################################################################################
class CustomLabel(QtGui.QLabel):
    """
    custom label za prikaz
    - omogucuje se selektiranje teksta misem
    - set boje backgrounda
    """
    def __init__(self, tekst='n/a', center=False, parent=None):
        QtGui.QLabel.__init__(self, parent=parent)
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard | QtCore.Qt.TextSelectableByMouse | QtCore.Qt.LinksAccessibleByMouse)
        self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        if center:
            self.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.setFont(font)
        self.set_color(QtGui.QColor(QtCore.Qt.white))
        self.setText(tekst)

    def set_color(self, boja):
        """
        Setter pozadinske boje gumba
        input parametrar boja je QColor
        """
        r = boja.red()
        g = boja.green()
        b = boja.blue()
        a = 100*boja.alpha()/255
        stil = "QLabel {background-color: rgba(" +"{0},{1},{2},{3}%)".format(r, g, b, a)+"}"
        self.setStyleSheet(stil)
################################################################################
################################################################################
class ReportTablicaKriterijaRiseFall(QtGui.QWidget):
    """
    tablica za kriterij vremena odaziva (uspon, pad..)
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent=parent)
        # definicija layouta
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setHorizontalSpacing(1)
        self.gridLayout.setVerticalSpacing(1)
        self.gridLayout.setContentsMargins(0,0,0,0)

        self.pos00 = CustomLabel(tekst='')
        self.pos01 = CustomLabel(tekst='<b> Naziv kriterija </b>', center=True)
        self.pos02 = CustomLabel(tekst='<b> Točka norme </b>', center=True)
        self.pos03 = CustomLabel(tekst='<b> Rezultati </b>', center=True)
        self.pos04 = CustomLabel(tekst='')
        self.pos05 = CustomLabel(tekst='<b> Uvijet prihvatljivosti </b>', center=True)
        self.pos06 = CustomLabel(tekst='<b> Ispunjeno </b>', center=True)
        self.pos10 = CustomLabel(tekst='<b> 1 </b>', center=True)
        self.pos20 = CustomLabel(tekst='<b> 2 </b>', center=True)
        self.pos30 = CustomLabel(tekst='<b> 3 </b>', center=True)
        self.pos11 = CustomLabel()
        self.pos12 = CustomLabel()
        self.pos13 = CustomLabel()
        self.pos14 = CustomLabel()
        self.pos15 = CustomLabel(center=True)
        self.pos16 = CustomLabel(center=True)
        self.pos21 = CustomLabel()
        self.pos22 = CustomLabel()
        self.pos23 = CustomLabel()
        self.pos24 = CustomLabel()
        self.pos25 = CustomLabel(center=True)
        self.pos26 = CustomLabel(center=True)
        self.pos31 = CustomLabel()
        self.pos32 = CustomLabel()
        self.pos33 = CustomLabel()
        self.pos34 = CustomLabel()
        self.pos35 = CustomLabel(center=True)
        self.pos36 = CustomLabel(center=True)

        self.gridLayout.addWidget(self.pos00, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.pos01, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.pos02, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.pos03, 0, 3, 1, 2)
        self.gridLayout.addWidget(self.pos05, 0, 5, 1, 1)
        self.gridLayout.addWidget(self.pos06, 0, 6, 1, 1)
        self.gridLayout.addWidget(self.pos10, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.pos20, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.pos30, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.pos11, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.pos12, 1, 2, 1, 1)
        self.gridLayout.addWidget(self.pos13, 1, 3, 1, 1)
        self.gridLayout.addWidget(self.pos14, 1, 4, 1, 1)
        self.gridLayout.addWidget(self.pos15, 1, 5, 1, 1)
        self.gridLayout.addWidget(self.pos16, 1, 6, 1, 1)
        self.gridLayout.addWidget(self.pos21, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.pos22, 2, 2, 1, 1)
        self.gridLayout.addWidget(self.pos23, 2, 3, 1, 1)
        self.gridLayout.addWidget(self.pos24, 2, 4, 1, 1)
        self.gridLayout.addWidget(self.pos25, 2, 5, 1, 1)
        self.gridLayout.addWidget(self.pos26, 2, 6, 1, 1)
        self.gridLayout.addWidget(self.pos31, 3, 1, 1, 1)
        self.gridLayout.addWidget(self.pos32, 3, 2, 1, 1)
        self.gridLayout.addWidget(self.pos33, 3, 3, 1, 1)
        self.gridLayout.addWidget(self.pos34, 3, 4, 1, 1)
        self.gridLayout.addWidget(self.pos35, 3, 5, 1, 1)
        self.gridLayout.addWidget(self.pos36, 3, 6, 1, 1)

        self.set_minimum_height_for_row(0, 30)
        self.set_minimum_height_for_row(1, 30)
        self.set_minimum_height_for_row(2, 30)
        self.set_minimum_height_for_row(3, 30)
        self.set_minimum_width_for_column(0, 30)
        self.set_minimum_width_for_column(1, 200)
        self.set_minimum_width_for_column(2, 75)
        self.set_minimum_width_for_column(3, 75)
        self.set_minimum_width_for_column(4, 75)
        self.set_minimum_width_for_column(5, 150)
        self.set_minimum_width_for_column(6, 75)

        # slaganje layouta u tablicu
        self.setLayout(self.gridLayout)

    def set_minimum_width_for_column(self, col, size):
        self.gridLayout.setColumnMinimumWidth(col, size)

    def set_minimum_height_for_row(self, row, size):
        self.gridLayout.setRowMinimumHeight(row, size)

    def find_needed_color(self, check):
        """
        helepr metoda koja vraca zelenu boju ako check ima vrijednost 'Da'. U
        protivnom vraca crvenu boju.
        """
        test = check
        test = test.lower()
        if test == 'da':
            color = QtGui.QColor(QtGui.QColor(0, 255, 0, 90))
        else:
            color = QtGui.QColor(QtGui.QColor(255, 0, 0, 90))
        return color

    def clear_results(self):
        """
        Clear rezultata tablice
        """
        #resert color
        self.set_row_background_color(QtGui.QColor(QtCore.Qt.white), 1)
        self.pos11.setText('')
        self.pos12.setText('')
        self.pos13.setText('')
        self.pos14.setText('')
        self.pos15.setText('')
        self.pos16.setText('')
        self.set_row_background_color(QtGui.QColor(QtCore.Qt.white), 2)
        self.pos21.setText('')
        self.pos22.setText('')
        self.pos23.setText('')
        self.pos24.setText('')
        self.pos25.setText('')
        self.pos26.setText('')
        self.set_row_background_color(QtGui.QColor(QtCore.Qt.white), 3)
        self.pos31.setText('')
        self.pos32.setText('')
        self.pos33.setText('')
        self.pos34.setText('')
        self.pos35.setText('')
        self.pos36.setText('')

    def set_values(self, data):
        """
        setter vrijednosti u tablicu
        3 reda .... koji idu kao dict... plin:{'rise':[], 'fall':[], 'diff':[]}
        Svaka lista ima komponente:
        [naziv, tocka norme, string oznake, vrijednost, uvijet prihvatljivosti, 'DA' ili 'NE']
        """
        self.clear_results()
        try:
            #rise
            self.pos11.setText(data['rise'][0])
            self.pos12.setText(data['rise'][1])
            self.pos13.setText(data['rise'][2])
            self.pos14.setText(str(round(data['rise'][3], 1)))
            self.pos15.setText(data['rise'][4])
            ispunjeno = data['rise'][5]
            self.pos16.setText(ispunjeno)
            color = self.find_needed_color(ispunjeno)
            self.set_row_background_color(color, 1)

            #fall
            self.pos21.setText(data['fall'][0])
            self.pos22.setText(data['fall'][1])
            self.pos23.setText(data['fall'][2])
            self.pos24.setText(str(round(data['fall'][3], 1)))
            self.pos25.setText(data['fall'][4])
            ispunjeno = data['fall'][5]
            self.pos26.setText(ispunjeno)
            color = self.find_needed_color(ispunjeno)
            self.set_row_background_color(color, 2)

            #rise - fall
            self.pos31.setText(data['diff'][0])
            self.pos32.setText(data['diff'][1])
            self.pos33.setText(data['diff'][2])
            self.pos34.setText(str(round(data['diff'][3], 1)))
            self.pos35.setText(data['diff'][4])
            ispunjeno = data['diff'][5]
            self.pos36.setText(ispunjeno)
            color = self.find_needed_color(ispunjeno)
            self.set_row_background_color(color, 3)
        except Exception as err:
            logging.error(str(err), exc_info=True)
            pass

    def set_row_background_color(self, color, red):
        """
        metoda za promjenu pozadinske boje reda u tablici
        ulazni parametar je boja (QColor) i red
        """
        if red == 1:
            self.pos10.set_color(color)
            self.pos11.set_color(color)
            self.pos12.set_color(color)
            self.pos13.set_color(color)
            self.pos14.set_color(color)
            self.pos15.set_color(color)
            self.pos16.set_color(color)
        elif red == 2:
            self.pos20.set_color(color)
            self.pos21.set_color(color)
            self.pos22.set_color(color)
            self.pos23.set_color(color)
            self.pos24.set_color(color)
            self.pos25.set_color(color)
            self.pos26.set_color(color)
        elif red == 3:
            self.pos30.set_color(color)
            self.pos31.set_color(color)
            self.pos32.set_color(color)
            self.pos33.set_color(color)
            self.pos34.set_color(color)
            self.pos35.set_color(color)
            self.pos36.set_color(color)
        else:
            pass
################################################################################
################################################################################
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
        ymin = min(y)
        ymax = max(y)
        delta = (ymax - ymin) / 20
        ymin = ymin - delta
        ymax = ymax + delta
        self.axes.set_ylim((ymin, ymax))
        #set horizontalni raspon
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
################################################################################
################################################################################
class RiseFallModel(QtCore.QAbstractTableModel):
    def __init__(self, frejm=None, naziv=None, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        if frejm is None:
            frejm = pd.DataFrame()
        self.set_frejm(frejm, naziv)

        self.high = 90.0 #LATER
        self.low = 10.0 #LATER

        self.CHECKABLE = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable
        self.DISABLED = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable
        self.SELECTABLE = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def set_high_limit(self, value):
        self.high = value
        self.layoutChanged.emit()

    def set_low_limit(self, value):
        self.low = value
        self.layoutChanged.emit()

    def expand_frejm(self, series, name):
        indeks = series.index
        expandedFrejm = pd.DataFrame(index=indeks)
        s1 = pd.Series(QtCore.Qt.Unchecked, index=indeks)
        naziv = '{0}-RISE'.format(name)
        expandedFrejm[naziv] = s1
        s2 = pd.Series(QtCore.Qt.Unchecked, index=indeks)
        naziv = '{0}-FALL'.format(name)
        expandedFrejm[naziv] = s2
        s3 = series
        expandedFrejm[name] = s3
        return expandedFrejm

    def set_frejm(self, series, name):
        self.dataFrejm = self.expand_frejm(series, name)
        self.layoutChanged.emit()

    def get_frejm(self):
        return self.dataFrejm.copy()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.dataFrejm)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.dataFrejm.columns)

    def flags(self, index):
        if index.isValid():
            col = index.column()
            red = index.row()
            nazivStupca = self.dataFrejm.columns[col]
            if 'RISE' in nazivStupca:
                value = self.dataFrejm.iloc[red, col+2]
                if value > self.low:
                    return self.DISABLED
                else:
                    return self.CHECKABLE
            elif 'FALL' in nazivStupca:
                value = self.dataFrejm.iloc[red, col+1]
                if value < self.high:
                    return self.DISABLED
                else:
                    return self.CHECKABLE
            else:
                return self.SELECTABLE

    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        nazivStupca = self.dataFrejm.columns[col]
        if 'RISE' in nazivStupca:
            if role == QtCore.Qt.DisplayRole:
                return ''
            elif role == QtCore.Qt.CheckStateRole:
                if self.dataFrejm.iloc[row, col] == 2:
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked
        elif 'FALL' in nazivStupca:
            if role == QtCore.Qt.DisplayRole:
                return ''
            elif role == QtCore.Qt.CheckStateRole:
                if self.dataFrejm.iloc[row, col] == 2:
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked
        else:
            if role == QtCore.Qt.DisplayRole:
                return round(float(self.dataFrejm.iloc[row, col]), 1)

    def setData(self, index, value, role):
        if not index.isValid() or role != QtCore.Qt.CheckStateRole:
            return None
        row = index.row()
        col = index.column()
        if value == 2:
            self.dataFrejm.iloc[row, col] = QtCore.Qt.Checked
        else:
            self.dataFrejm.iloc[row, col] = QtCore.Qt.Unchecked
        self.dataChanged.emit(index, index)
        return True

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return str(self.dataFrejm.index[section].time())
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return str(self.dataFrejm.columns[section])
################################################################################
################################################################################
class RiseFallResultModel(QtCore.QAbstractTableModel):
    def __init__(self, frejm=None, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)

        stupci = ['Naziv', 'Pocetak', 'Kraj', 'Delta']
        if frejm is None:
            frejm = pd.DataFrame(columns=stupci)
        self.set_frejm(frejm)

    def set_frejm(self, frejm):
        self.frejm = frejm
        self.layoutChanged.emit()

    def get_frejm(self):
        return self.frejm.copy()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.frejm)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.frejm.columns)

    def flags(self, index):
        if index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        if role == QtCore.Qt.DisplayRole:
            return str(self.frejm.iloc[row, col])

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return str(self.frejm.columns[section])
################################################################################
################################################################################
class RiseFallWidget(QtGui.QWidget):
    """
    prozor provjeru vremena uspona i pada za pojedini plin
    """
    def __init__(self, parent=None, dokument=None, frejm=None, naziv=None):
        """
        inicijalizacija prozora uz instancu dokumenta i slajs frejma sa podacima
        """
        QtGui.QWidget.__init__(self, parent=parent)

        self.doc = dokument
        self.frejm = frejm
        self.naziv = naziv
        self.checkSpremi = False
        self.rezultatStupci = ['Naziv', 'Pocetak', 'Kraj', 'Delta']
        self.rezultat = pd.DataFrame(columns=self.rezultatStupci)
        self.meta = {'xlabel':'vrijeme',
                     'ylabel':'koncentracija',
                     'title':'Vrijeme uspona i pada'}
        #TODO! nedostaje rest informacija o granicnim vrijednostima analiticke metode za uredjaj
        kriterijRise = ['Vrijeme odaziva (uspon)',
                        '???',
                        't<sub>r</sub',
                        np.NaN,
                        '???',
                        'NE']
        kriterijFall = ['Vrijeme odaziva (pad)',
                        '???',
                        't<sub>f</sub',
                        np.NaN,
                        '???',
                        'NE']
        kriterijDiff = ['Razlika odaziva uspona i pada',
                        '???',
                        't<sub>d</sub',
                        np.NaN,
                        '???',
                        'NE']
        self.reportValue = {'rise':kriterijRise,
                            'fall':kriterijFall,
                            'diff':kriterijDiff}

        self.lowLimit = 10.0 #LATER potegnuti iz dokumenta / default?
        self.highLimit = 90.0 #LATER potegnuti iz dokumenta / default?
        self.model = RiseFallModel(frejm=self.frejm, naziv=self.naziv)
        self.model.set_high_limit(self.highLimit)
        self.model.set_low_limit(self.lowLimit)
        self.modelRezultata = RiseFallResultModel()

        #widgeti
        self.tablicaPodataka = QtGui.QTableView()
        self.tablicaPodataka.setModel(self.model)
        self.tablicaRezultata = QtGui.QTableView()
        self.tablicaRezultata.setModel(self.modelRezultata)
        self.tablicaPodataka.setMinimumWidth(350)
        self.tablicaPodataka.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.tablicaRezultata.setMinimumWidth(350)
        self.tablicaRezultata.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.lowLimitLabel = QtGui.QLabel('Niži prag :')
        self.highLimitLabel = QtGui.QLabel('Viši prag :')
        self.spinBoxHigh = QtGui.QDoubleSpinBox()
        self.spinBoxHigh.setRange(-5000.0, 5000.0)
        self.spinBoxHigh.setValue(self.highLimit)
        self.spinBoxLow = QtGui.QDoubleSpinBox()
        self.spinBoxLow.setRange(-5000.0, 5000.0)
        self.spinBoxLow.setValue(self.lowLimit)
        self.graf = RiseFallKanvas(meta=self.meta)
        self.tablicaKriterija = ReportTablicaKriterijaRiseFall()
        self.checkBoxAktivnosti = QtGui.QCheckBox()
        self.checkBoxLabel = QtGui.QLabel('Aktiviraj komponentu :')

        #layout
        glavniLayout = QtGui.QHBoxLayout()
        kontrolniLayout = QtGui.QVBoxLayout()
        spinLayout = QtGui.QGridLayout()
        rezultatLayout = QtGui.QVBoxLayout()
        spinLayout.addWidget(self.checkBoxLabel, 0, 0)
        spinLayout.addWidget(self.checkBoxAktivnosti, 0, 1)
        spinLayout.addWidget(self.lowLimitLabel, 1, 0)
        spinLayout.addWidget(self.spinBoxLow, 1, 1)
        spinLayout.addWidget(self.highLimitLabel, 2, 0)
        spinLayout.addWidget(self.spinBoxHigh, 2, 1)
        kontrolniLayout.addLayout(spinLayout)
        kontrolniLayout.addWidget(self.tablicaPodataka)
        rezultatLayout.addWidget(self.graf)
        rezultatLayout.addWidget(self.tablicaRezultata)
        rezultatLayout.addWidget(self.tablicaKriterija)
        glavniLayout.addLayout(kontrolniLayout)
        glavniLayout.addLayout(rezultatLayout)
        self.setLayout(glavniLayout)

        #connections
        self.tablicaPodataka.clicked.connect(self.check_pocetak)
        self.spinBoxHigh.valueChanged.connect(self.modify_high_limit)
        self.spinBoxLow.valueChanged.connect(self.modify_low_limit)
        self.checkBoxAktivnosti.toggled.connect(self.aktiviraj_komponentu)

        #refresh izgled
        self.update_rezultate()
        self.aktiviraj_komponentu(self.checkSpremi)

    def aktiviraj_komponentu(self, x):
        self.checkSpremi = x
        if x:
            self.spinBoxHigh.setEnabled(True)
            self.spinBoxLow.setEnabled(True)
            self.tablicaKriterija.setEnabled(True)
            self.tablicaPodataka.setEnabled(True)
            self.tablicaRezultata.setEnabled(True)
        else:
            self.spinBoxHigh.setEnabled(False)
            self.spinBoxLow.setEnabled(False)
            self.tablicaKriterija.setEnabled(False)
            self.tablicaPodataka.setEnabled(False)
            self.tablicaRezultata.setEnabled(False)

    def modify_high_limit(self, x):
        value = float(x)
        self.highLimit = value
        self.model.set_high_limit(value)
        self.update_rezultate()

    def modify_low_limit(self, x):
        value = float(x)
        self.lowLimit = value
        self.model.set_low_limit(value)
        self.update_rezultate()

    def check_pocetak(self, x):
        red = x.row()
        stupac = x.column()
        check = self.model.dataFrejm.iloc[red, stupac]
        nazivStupca = self.model.dataFrejm.columns[stupac]
        start = self.model.dataFrejm.index[red]
        if check == QtCore.Qt.Checked:
            if 'RISE' in nazivStupca:
                col = stupac + 2
                kraj = self.nadji_kraj_uspona(red, col)
                if not isinstance(kraj, pd.tslib.NaTType):
                    delta = (kraj - start).total_seconds()
                else:
                    delta = np.NaN
                self.dodaj_red_u_rezultat_frejm(nazivStupca, start, kraj, delta)
            elif 'FALL' in nazivStupca:
                col = stupac + 1
                kraj = self.nadji_kraj_pada(red, col)
                if not isinstance(kraj, pd.tslib.NaTType):
                    delta = (kraj - start).total_seconds()
                else:
                    delta = np.NaN
                self.dodaj_red_u_rezultat_frejm(nazivStupca, start, kraj, delta)
            else:
                pass
        elif check == QtCore.Qt.Unchecked:
            self.makni_red_iz_rezultat_frejma(nazivStupca, start)
        else:
            pass

    def nadji_kraj_uspona(self, red, stupac):
        frejm = self.model.dataFrejm.copy()
        nazivStupca = frejm.columns[stupac]
        frejm = frejm[nazivStupca]
        frejm = frejm[frejm.index >= frejm.index[red]]
        frejm = frejm[frejm >= self.highLimit]
        if len(frejm):
            return frejm.index[0]
        else:
            return pd.NaT

    def nadji_kraj_pada(self, red, stupac):
        frejm = self.model.dataFrejm.copy()
        nazivStupca = frejm.columns[stupac]
        frejm = frejm[nazivStupca]
        frejm = frejm[frejm.index >= frejm.index[red]]
        frejm = frejm[frejm <= self.lowLimit]
        if len(frejm):
            return frejm.index[0]
        else:
            return pd.NaT

    def dodaj_red_u_rezultat_frejm(self, nazivStupca, start, kraj, delta):
        indeks = len(self.rezultat)
        #provjeri da li postoji vec isto vrijeme prije dodavanja
        startovi = list(self.rezultat['Pocetak'])
        if start not in startovi:
            df = pd.DataFrame({'Naziv':nazivStupca,
                               'Pocetak':start,
                               'Kraj':kraj,
                               'Delta':delta},
                               index=[indeks],
                               columns=self.rezultatStupci)
            self.rezultat = self.rezultat.append(df)
            self.update_rezultate()

    def makni_red_iz_rezultat_frejma(self, nazivStupca, start):
        if len(self.rezultat):
            frejm = self.rezultat.copy()
            frejm = frejm[frejm.iloc[:,0]==nazivStupca]
            frejm = frejm[frejm.iloc[:,1]==start]
            self.rezultat = self.rezultat.drop(self.rezultat.index[frejm.index])
            #reindex
            self.rezultat.index = list(range(len(self.rezultat)))
            self.update_rezultate()

    def update_rezultate(self):
        self.modelRezultata.set_frejm(self.rezultat)
        self.graf.crtaj(podaci=self.frejm,
                        rezultati=self.rezultat,
                        high=self.highLimit,
                        low=self.lowLimit)
        self.set_reportValue()

    def get_postavke_za_dokument(self):
        output = {
            'rezultati':self.rezultat,
            'lowLimit':self.lowLimit,
            'highLimit':self.highLimit,
            'check':self.checkSpremi}
        return output

    def set_postavke_iz_dokumenta(self, mapa):
        self.spinBoxHigh.setValue(mapa['highLimit'])
        self.spinBoxLow.setValue(mapa['lowLimit'])
        self.checkBoxAktivnosti.setChecked(mapa['check'])
        frejm = mapa['rezultati'].copy()
        risenaziv = '{0}-RISE'.format(self.naziv)
        fallnaziv = '{0}-FALL'.format(self.naziv)
        frejmRise = frejm[frejm.loc[:,'Naziv'] == risenaziv]
        frejmFall = frejm[frejm.loc[:,'Naziv'] == fallnaziv]
        #prebaciti model u checked stanje za zadane indekse
        indeksiRise = list(frejmRise.index)
        indeksiFall = list(frejmFall.index)
        for i in indeksiRise:
            self.model.dataFrejm.loc[i, risenaziv] = QtCore.Qt.Checked
        for i in indeksiFall:
            self.model.dataFrejm.loc[i, fallnaziv] = QtCore.Qt.Checked
        self.set_reportValue()

    def set_reportValue(self):
        frejm = self.rezultat.copy()
        risenaziv = '{0}-RISE'.format(self.naziv)
        fallnaziv = '{0}-FALL'.format(self.naziv)
        frejmRise = frejm[frejm.loc[:,'Naziv'] == risenaziv]
        frejmFall = frejm[frejm.loc[:,'Naziv'] == fallnaziv]
        #time rise
        if len(frejmRise):
            deltaRise = np.average(frejmRise.loc[:,'Delta'])
        else:
            deltaRise = np.NaN
        self.reportValue['rise'][3] = deltaRise
        #TODO! treba prebaciti i [5] element u DA ili NE ovisno o kriteriju + mora biti vise od 4 tocke

        #time fall
        if len(frejmFall):
            deltaFall = np.average(frejmFall.loc[:,'Delta'])
        else:
            deltaFall = np.NaN
        self.reportValue['fall'][3] = deltaFall
        #TODO! treba prebaciti i [5] element u DA ili NE ovisno o kriteriju

        # time rise - time fall
        if (not np.isnan(deltaRise)) and (not np.isnan(deltaFall)):
            t = abs(deltaRise - deltaFall)
        else:
            t = np.NaN
        self.reportValue['diff'][3] = t
        #TODO! treba prebaciti i [5] element u DA ili NE ovisno o kriteriju

        self.tablicaKriterija.set_values(self.reportValue)

################################################################################
################################################################################
class RiseFallGlavniProzor(QtGui.QWidget):
    """
    Glavni prozor za odredjivanje vremena uspona i pada.
    """
    def __init__(self, parent=None, dokument=None):
        """
        inicijalizacija prozora uz instancu dokumenta
        """
        QtGui.QWidget.__init__(self, parent=parent)

        self.doc = dokument
        self.dictTabova = {}
        self.podaci = pd.DataFrame()

        #widgeti
        self.loadFrejmGumb = QtGui.QPushButton('Ucitaj podatke')
        self.tabWidget = QtGui.QTabWidget()

        #layout setup
        glavniLayout = QtGui.QVBoxLayout()
        layout1 = QtGui.QHBoxLayout()
        layout2 = QtGui.QHBoxLayout()
        layout1.addWidget(self.loadFrejmGumb)
        layout1.addStretch(-1)
        layout2.addWidget(self.tabWidget)
        glavniLayout.addLayout(layout1)
        glavniLayout.addLayout(layout2)
        self.setLayout(glavniLayout)

        # poveznice
        self.setup_connections()

    def setup_connections(self):
        """povezivanje signala i slotova unutar prozora"""
        self.loadFrejmGumb.clicked.connect(self.ucitaj_podatke)

    def get_podatke_za_spremanje_taba(self):
        """Pakiranje bitnih podataka za save u nested dict strukturu.
        kljucevi su:
        --> 'Podaci': dataframe sirovih podataka s kojima se radi
        --> 'naziv stupca u frejmu sirovih podataka': dict
            --> 'rezultati' :frejm sa podacima o izboru pocetka i kraja uspona i padova
            --> 'lowLimit' : niza granica (trigger za kraj pada)
            --> 'highLimit' : visa granica (trigger za kraj uspona)
            --> 'check' : check da li je komponenta aktivna za rad (i za report)
        """
        output = {}
        output['Podaci'] = self.podaci
        for tab in self.dictTabova:
            widget = self.dictTabova[tab]
            data = widget.get_postavke_za_dokument()
            output[tab] = data
        return output

    def set_podatke_za_rekonstrukciju_taba(self, mapa):
        """naredba za rekonstrukciju svih prozora unutar taba prilikom loada
        iz spremljenog filea"""
        #clear postojece tabove
        self.clear_tabove()
        #rekonstrukcija tabova
        self.podaci = mapa['Podaci']
        stupci = self.podaci.columns
        for stupac in stupci:
            slajs = self.podaci[stupac].copy()
            tab = RiseFallWidget(dokument=self.doc, frejm=slajs, naziv=stupac)
            #rekonstrukcija stanja pojedinog taba
            tab.set_postavke_iz_dokumenta(mapa[stupac])
            self.dictTabova[stupac] = tab
            self.tabWidget.addTab(tab, stupac)

    def clear_tabove(self):
        """brisanje postojecih tabova"""
        # makni tabove sa reultatima
        for tab in self.dictTabova:
            widget = self.dictTabova[tab]
            self.tabWidget.removeTab(self.tabWidget.indexOf(widget))
        # izbrisi sve objekte sa rezultatima
        for key in self.dictTabova:
            sip.delete(self.dictTabova[key])
            self.dictTabova[key] = None
        # force garbage collection
        self.dictTabova = {}
        gc.collect()

    def ucitaj_podatke(self):
        """dijalog za ucitavanje csv fileova sa podacima"""
        filepath = QtGui.QFileDialog.getOpenFileName(parent=self,
                                                     caption='Ucitaj file sa podacima',
                                                     filter='csv files (*.csv);;all (*.*)')
        if filepath:
            self.clear_tabove()
            self.podaci = pd.read_csv(filepath,
                                      encoding='utf-8',
                                      index_col=0,
                                      parse_dates=True)
            stupci = self.podaci.columns
            for stupac in stupci:
                slajs = self.podaci[stupac].copy()
                tab = RiseFallWidget(dokument=self.doc, frejm=slajs, naziv=stupac)
                self.dictTabova[stupac] = tab
                self.tabWidget.addTab(tab, stupac)

################################################################################
################################################################################
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = RiseFallGlavniProzor()
    window.show()
    sys.exit(app.exec_())
