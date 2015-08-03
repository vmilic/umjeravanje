# -*- coding: utf-8 -*-
"""
Created on Mon May 18 13:53:03 2015

@author: DHMZ-Milic
"""
import pandas as pd
from PyQt4 import QtCore, QtGui


class SiroviFrameModel(QtCore.QAbstractTableModel):
    """
    Model sa sirovim podacima za umjeravanje
    """
    def __init__(self, frejm=None, tocke=None, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        if frejm is None:
            frejm = pd.DataFrame()
        if tocke is None:
            tocke = []
        self.set_frejm(frejm)
        self.set_tocke(tocke)
        self.startIndeks = 0

    def set_frejm(self, frejm):
        """Setter za frejm sirovih podataka."""
        self.dataFrejm = frejm
        self.layoutChanged.emit()

    def set_tocke(self, tocke):
        """Setter za listu umjernih tocaka."""
        self.tocke = tocke
        self.layoutChanged.emit()

    def set_start(self, indeks):
        """Setter pocetka umjeravanja, integer"""
        n = int(indeks.row()) #redni broj indeksa
        delta = n - self.startIndeks #odmak od prijasnjeg starta
        for tocka in self.tocke:
            value = set([ind + delta for ind in list(tocka.indeksi)])
            tocka.indeksi = value
        self.startIndeks = n
        self.layoutChanged.emit()

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        MUST BE IMPLEMENTED.
        Return number of rows of pandas dataframe
        """
        return len(self.dataFrejm)

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        MUST BE IMPLEMENTED
        Return number of columns of pandas dataframe. (add one for time index)
        """
        return len(self.dataFrejm.columns)

    def flags(self, index):
        """
        Flags each item in table as enabled and selectable
        """
        if index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        """
        MUST BE IMPLEMENTED.
        Return value for each index and role
        """
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        if role == QtCore.Qt.DisplayRole:
            return round(float(self.dataFrejm.iloc[row, col]), 2)
        if role == QtCore.Qt.BackgroundColorRole:
            for tocka in self.tocke:
                if tocka.test_indeks_unutar_tocke(row):
                    return QtGui.QBrush(tocka.boja)
            if row == self.startIndeks:
                brush = QtGui.QBrush()
                brush.setColor(QtGui.QColor(0, 0, 0, 80))
                brush.setStyle(QtCore.Qt.FDiagPattern)
                return brush
            elif row > self.startIndeks:
                brush = QtGui.QBrush()
                brush.setColor(QtGui.QColor(0, 0, 0, 80))
                brush.setStyle(QtCore.Qt.Dense6Pattern)
                return brush
            else:
                return QtGui.QBrush(QtGui.QColor(255, 255, 255, 255))

    def headerData(self, section, orientation, role):
        """
        Sets the headers of the table...
        """
        if orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return str(self.dataFrejm.index[section].time())
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return str(self.dataFrejm.columns[section])


class TockeModel(QtCore.QAbstractTableModel):
    """
    Model sa podacima o tockama
    """
    def __init__(self, frejm=None, tocke=None, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        if frejm is None:
            frejm = pd.DataFrame()
        if tocke is None:
            tocke = []
        self.headeri = ['Naziv',
                        'Cref [0,1]',
                        'Pocetni indeks',
                        'Zavrsni indeks',
                        'Broj minutnih podataka',
                        'Broj tocaka',
                        'Boja']
        self.set_frejm(frejm)
        self.set_tocke(tocke)

    def set_frejm(self, frejm):
        """Setter za frejm sirovih podataka."""
        self.dataFrejm = frejm
        self.layoutChanged.emit()

    def set_tocke(self, tocke):
        """Setter za listu umjernih tocaka."""
        self.tocke = tocke
        self.layoutChanged.emit()

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        MUST BE IMPLEMENTED.
        Return number of rows of pandas dataframe
        """
        return len(self.tocke)

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        MUST BE IMPLEMENTED
        Return number of columns of pandas dataframe. (add one for time index)
        """
        return len(self.headeri)

    def flags(self, index):
        """
        Flags each item in table as enabled and selectable
        """
        if index.isValid():
            col = index.column()
            if col in [0, 1, 6]:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
            else:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        """
        MUST BE IMPLEMENTED.
        Return value for each index and role
        """
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if col == 0:
                return str(self.tocke[row])
            elif col == 1:
                return round(self.tocke[row].crefFaktor, 3)
            elif col == 2:
                start = min(self.tocke[row].indeksi)
                try:
                    return str(self.dataFrejm.index[start].time())
                except LookupError:
                    return 'Izvan granica'
            elif col == 3:
                kraj = max(self.tocke[row].indeksi)
                try:
                    return str(self.dataFrejm.index[kraj].time())
                except LookupError:
                    return 'Izvan granica'
            elif col == 4:
                return len(self.tocke[row].indeksi)
            elif col == 5:
                value = int(len(self.tocke[row].indeksi)/3)
                if value >= 5:
                    return value
                else:
                    return 'Nedovoljan broj tocaka'
        if role == QtCore.Qt.BackgroundColorRole:
            return QtGui.QBrush(self.tocke[row].boja)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """
        Metoda zaduzena za postavljanje novih vrijednosti u model(editable).
        """
        if not index.isValid():
            return False

        if role == QtCore.Qt.EditRole:
            row = index.row()
            col = index.column()
            if col == 0:
                self.tocke[row].ime = str(value)
                self.emit(QtCore.SIGNAL('promjena_vrijednosti_tocke'))
                return True
            elif col == 1:
                try:
                    v = float(value)
                except Exception:
                    return False
                if v >= 0.0 and v <= 1.0:
                    self.tocke[row].crefFaktor = v
                    self.emit(QtCore.SIGNAL('promjena_vrijednosti_tocke'))
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False


    def headerData(self, section, orientation, role):
        """
        Sets the headers of the table...
        """
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return str(self.headeri[section])


class RezultatModel(QtCore.QAbstractTableModel):
    """
    Model tablica za rezultate umjeeravanja
    """
    def __init__(self, frejm=None, parent=None):
        """
        Initialize with pandas dataframe
        """
        QtCore.QAbstractTableModel.__init__(self, parent)
        if frejm == None:
            self.dataFrejm = pd.DataFrame()
        else:
            self.dataFrejm = frejm

    def set_frejm(self, frejm):
        """
        seter za podatke
        """
        self.dataFrejm = frejm
        self.layoutChanged.emit()

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        MUST BE IMPLEMENTED.
        Return number of rows of pandas dataframe
        """
        return len(self.dataFrejm)

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        MUST BE IMPLEMENTED
        Return number of columns of pandas dataframe. (add one for time index)
        """
        return len(self.dataFrejm.columns)

    def flags(self, index):
        """
        Flags each item in table as enabled and selectable
        """
        if index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        """
        MUST BE IMPLEMENTED.
        Return value for each index and role
        """
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        if role == QtCore.Qt.DisplayRole:
            value = self.dataFrejm.iloc[row, col]
            if type(value) != str:
                return round(float(value), 2)
            else:
                return value

    def headerData(self, section, orientation, role):
        """
        Sets the headers of the table...
        """
        if orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return str(self.dataFrejm.index[section])
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return str(self.dataFrejm.columns[section])


class KonverterTockeModel(QtCore.QAbstractTableModel):
    """
    Model sa podacima o tockama
    """
    def __init__(self, frejm=None, tocke=None, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        if frejm is None:
            frejm = pd.DataFrame()
        if tocke is None:
            tocke = []
        self.headeri = ['Naziv',
                        'Pocetni indeks',
                        'Zavrsni indeks',
                        'Broj minutnih podataka',
                        'Broj tocaka',
                        'Boja']
        self.set_frejm(frejm)
        self.set_tocke(tocke)

    def set_frejm(self, frejm):
        """Setter za frejm sirovih podataka."""
        self.dataFrejm = frejm
        self.layoutChanged.emit()

    def set_tocke(self, tocke):
        """Setter za listu umjernih tocaka."""
        self.tocke = tocke
        self.layoutChanged.emit()

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        MUST BE IMPLEMENTED.
        Return number of rows of pandas dataframe
        """
        return len(self.tocke)

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        MUST BE IMPLEMENTED
        Return number of columns of pandas dataframe. (add one for time index)
        """
        return len(self.headeri)

    def flags(self, index):
        """
        Flags each item in table as enabled and selectable
        """
        if index.isValid():
            col = index.column()
            if col in [0, 5]:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
            else:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        """
        MUST BE IMPLEMENTED.
        Return value for each index and role
        """
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if col == 0:
                return str(self.tocke[row])
            elif col == 1:
                start = min(self.tocke[row].indeksi)
                try:
                    return str(self.dataFrejm.index[start].time())
                except LookupError:
                    return 'Izvan granica'
            elif col == 2:
                kraj = max(self.tocke[row].indeksi)
                try:
                    return str(self.dataFrejm.index[kraj].time())
                except LookupError:
                    return 'Izvan granica'
            elif col == 3:
                return len(self.tocke[row].indeksi)
            elif col == 4:
                value = int(len(self.tocke[row].indeksi)/3)
                if value >= 5:
                    return value
                else:
                    return 'Nedovoljan broj tocaka'
        if role == QtCore.Qt.BackgroundColorRole:
            return QtGui.QBrush(self.tocke[row].boja)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """
        Metoda zaduzena za postavljanje novih vrijednosti u model(editable).
        """
        if not index.isValid():
            return False

        if role == QtCore.Qt.EditRole:
            row = index.row()
            col = index.column()
            if col == 0:
                self.tocke[row].ime = str(value)
                self.emit(QtCore.SIGNAL('promjena_vrijednosti_konverter_tocke'))
                return True
            else:
                return False
        else:
            return False

    def headerData(self, section, orientation, role):
        """
        Sets the headers of the table...
        """
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return str(self.headeri[section])


class KonverterFrameModel(QtCore.QAbstractTableModel):
    """
    Model sa sirovim podacima za umjeravanje
    """
    def __init__(self, frejm=None, tocke=None, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        if frejm is None:
            frejm = pd.DataFrame()
        if tocke is None:
            tocke = []
        self.set_frejm(frejm)
        self.set_tocke(tocke)
        self.startIndeks = 0

    def set_frejm(self, frejm):
        """Setter za frejm sirovih podataka."""
        self.dataFrejm = frejm
        self.layoutChanged.emit()

    def set_tocke(self, tocke):
        """Setter za listu umjernih tocaka."""
        self.tocke = tocke
        self.layoutChanged.emit()

    def set_start(self, indeks):
        """Setter pocetka umjeravanja, integer"""
        n = int(indeks.row()) #redni broj indeksa
        delta = n - self.startIndeks #odmak od prijasnjeg starta
        for tocka in self.tocke:
            value = set([ind + delta for ind in list(tocka.indeksi)])
            tocka.indeksi = value
        self.startIndeks = n
        self.layoutChanged.emit()

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        MUST BE IMPLEMENTED.
        Return number of rows of pandas dataframe
        """
        return len(self.dataFrejm)

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        MUST BE IMPLEMENTED
        Return number of columns of pandas dataframe. (add one for time index)
        """
        return len(self.dataFrejm.columns)

    def flags(self, index):
        """
        Flags each item in table as enabled and selectable
        """
        if index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        """
        MUST BE IMPLEMENTED.
        Return value for each index and role
        """
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        if role == QtCore.Qt.DisplayRole:
            return round(float(self.dataFrejm.iloc[row, col]), 2)
        if role == QtCore.Qt.BackgroundColorRole:
            for tocka in self.tocke:
                if tocka.test_indeks_unutar_tocke(row):
                    return QtGui.QBrush(tocka.boja)
            if row == self.startIndeks:
                brush = QtGui.QBrush()
                brush.setColor(QtGui.QColor(0, 0, 0, 80))
                brush.setStyle(QtCore.Qt.FDiagPattern)
                return brush
            elif row > self.startIndeks:
                brush = QtGui.QBrush()
                brush.setColor(QtGui.QColor(0, 0, 0, 80))
                brush.setStyle(QtCore.Qt.Dense6Pattern)
                return brush
            else:
                return QtGui.QBrush(QtGui.QColor(255, 255, 255, 255))

    def headerData(self, section, orientation, role):
        """
        Sets the headers of the table...
        """
        if orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return str(self.dataFrejm.index[section].time())
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return str(self.dataFrejm.columns[section])
