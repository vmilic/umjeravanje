# -*- coding: utf-8 -*-
"""
Created on Mon May 18 13:53:03 2015

@author: DHMZ-Milic
"""
import pandas as pd
from PyQt4 import QtCore, QtGui


class ComboBoxDelegate(QtGui.QItemDelegate):
    def __init__(self, stupci=['None'], parent=None):
        QtGui.QItemDelegate.__init__(self, parent=parent)
        self.stupci = stupci

    def createEditor(self, parent, option, index):
        """
        return editor widget

        parent
        --> argument sluzi da stvoreni editor ne bude "garbage collected" (parent drzi referencu na njega)
        option
        --> Qt style opcije... nebitno (ali mora biti kao positional argument)
        index
        --> indeks elementa iz tablice (veza sa modelom)
        """
        editor = QtGui.QComboBox(parent=parent)
        editor.clear()
        editor.addItems(sorted(self.stupci))
        ind = editor.findText('None')
        editor.setCurrentIndex(ind)
        editor.setFocusPolicy(QtCore.Qt.StrongFocus)
        return editor

    def setEditorData(self, editor, index):
        """
        Inicijalizacija editora sa podacima, setup izgleda editora
        """
        pass

    def setModelData(self, editor, model, index):
        """
        Nakon kraja editiranja, metoda postavlja novo unesenu vrijednost u model
        """
        data = str(editor.currentText())
        model.setData(index, data)


class ColorDelegate(QtGui.QItemDelegate):
    """
    Delegat klasa za tockeView, stupac 6 (promjena boje preko dijaloga)
    """
    def __init__(self, tocke=None, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)
        self.tocke = tocke

    def createEditor(self, parent, option, index):
        """
        Direktni poziv dijaloga i ako se vrati ok boja, direktni setter podataka
        """
        if index.isValid():
            red = index.row()
            oldColor = self.tocke[red].boja.rgba()
            newColor, test = QtGui.QColorDialog.getRgba(oldColor)
            if test:
                color = QtGui.QColor().fromRgba(newColor)
                self.tocke[red].boja = color
                #signaliziraj za refresh viewova
                self.emit(QtCore.SIGNAL('promjena_boje_tocke'))


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
        if isinstance(indeks, QtCore.QModelIndex):
            n = int(indeks.row()) #redni broj indeksa
        else:
            n = indeks
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
    def __init__(self, frejm=None, tocke=None, parent=None):
        """
        Initialize with pandas dataframe
        """
        QtCore.QAbstractTableModel.__init__(self, parent)
        if frejm == None:
            self.dataFrejm = pd.DataFrame()
        else:
            self.dataFrejm = frejm
        self.tocke = tocke

    def set_frejm(self, frejm):
        """
        seter za podatke
        """
        self.dataFrejm = frejm
        self.layoutChanged.emit()

    def set_tocke(self, tocke):
        """
        setter za tocke
        """
        self.tocke = tocke
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
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            value = self.dataFrejm.iloc[row, col]
            if not isinstance(value, str):
                value = round(value, 3)
            return str(value)
        if role == QtCore.Qt.BackgroundColorRole:
            return self.tocke[row].boja

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


class RezultatParametriModel(QtCore.QAbstractTableModel):
    """
    Model tablica za rezultate umjeeravanja
    """
    def __init__(self, lista=None, parent=None):
        """
        Initialize with pandas dataframe
        """
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.headeri = ['Naziv',
                        'Min. granica',
                        'Vrijednost',
                        'Max. granica']
        self.set_lista(lista)

    def set_lista(self, lista):
        """
        seter za podatke
        """
        self.lista = lista
        self.layoutChanged.emit()

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        MUST BE IMPLEMENTED.
        Return number of rows of pandas dataframe
        """
        return len(self.lista)

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        MUST BE IMPLEMENTED
        Return number of columns of pandas dataframe. (add one for time index)
        """
        return 4

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
            value = self.lista[row][col]
            if not isinstance(value, str):
                value = round(value, 3)
            return str(value)
        if role == QtCore.Qt.ToolTipRole:
            return str(self.lista[row][col])
        if role == QtCore.Qt.BackgroundColorRole:
            test = self.lista[row][4]
            if test:
                return QtGui.QBrush(QtGui.QColor(0, 255, 0, 90))
            else:
                return QtGui.QBrush(QtGui.QColor(255, 0, 0, 90))

    def headerData(self, section, orientation, role):
        """
        Sets the headers of the table...
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(self.headeri[section])


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

class BaseFrejmModel(QtCore.QAbstractTableModel):
    """
    Definiranje qt modela za qt table view klase.
    Osnova modela ce biti pandas dataframe.
    Must reimplement:
        rowCount()
        columnCount()
        data()
        headerData()
    Implemented by default:
        parent()
        index()
    """
    def __init__(self, frejm=pd.DataFrame(), parent=None):
        """
        Initialize with pandas dataframe with data
        """
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.dataFrejm = frejm
        self.cols = ['None' for i in range(len(frejm.columns))]

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        MUST BE IMPLEMENTED.
        Return number of rows of pandas dataframe
        """
        return len(self.dataFrejm)+1
        #return min(15, len(self.dataFrejm))+1 #prikaz max 15 vrijednosti u tablici

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
            if index.row() == 0:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
            else:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """
        must be enabled for editable models
        """
        if not index.isValid():
            return False

        row = index.row()
        col = index.column()
        if role == QtCore.Qt.EditRole and row == 0:
            self.cols[col] = str(value)
            """emit sigala da je doslo do promjene u modelu. View se nece
            updateati sve dokle god je fokus na comboboxu (smatra da editing
            nije gotov)."""
            self.dataChanged.emit(index, index)
            return True
        else:
            return False

    def data(self, index, role):
        """
        MUST BE IMPLEMENTED.
        Return value for each index and role
        """
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        if row == 0:
            if role == QtCore.Qt.DisplayRole:
                return self.cols[col]
        else:
            if role == QtCore.Qt.DisplayRole:
                return round(float(self.dataFrejm.iloc[row-1, col]),2)

    def headerData(self, section, orientation, role):
        """
        Sets the headers of the table...
        """
        if orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                if section == 0:
                    return 'Vrijeme'
                else:
                    return str(self.dataFrejm.index[section-1])
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return str(self.dataFrejm.columns[section])


class PostajaUredjajKomponentaModel(QtCore.QAbstractTableModel):
    def __init__(self, lista=None, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.headeri = ['Postaja', 'Uredjaj', 'Komponenta']
        self.set_lista(lista)

    def set_lista(self, x):
        self.lista = x
        self.layoutChanged.emit()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.lista)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 3

    def flags(self, index):
        if index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        if role == QtCore.Qt.DisplayRole:
            return str(self.lista[row][col])

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return str(self.headeri[section])

