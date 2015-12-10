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
    def __init__(self, frejm=None, tocke=None, start=0, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        if frejm is None:
            frejm = pd.DataFrame()
        if tocke is None:
            tocke = []
        self.endIndeks = 0
        self.set_frejm(frejm)
        self.set_tocke(tocke)
        self.set_start(start)

    def set_frejm(self, frejm):
        """Setter za frejm sirovih podataka."""
        self.dataFrejm = frejm
        self.layoutChanged.emit()

    def get_frejm(self):
        """getter za frejm sirovih podataka."""
        return self.dataFrejm

    def set_tocke(self, tocke):
        """Setter za listu umjernih tocaka."""
        self.tocke = tocke
        ind = min([min(i.indeksi) for i in self.tocke])
        # odmakni pocetak za 15 redova prije od najmanjeg indeksa tocke, ako je moguce
        if ind-15 < 0:
            self.startIndeks = 0
        else:
            self.startIndeks = ind - 15
        self.endIndeks = max([max(i.indeksi) for i in self.tocke])
        self.layoutChanged.emit()

    def get_tocke(self):
        """getter za listu umjernih tocaka."""
        return self.tocke

    def translatiraj_tocke(self, x):
        """translacija izabranih tocaka za x redova. Ulazni parametar x je novi
        pocetni indeks."""
        delta = x - self.startIndeks
        for tocka in self.tocke:
            value = set([ind + delta for ind in list(tocka.indeksi)])
            tocka.indeksi = value

    def set_start(self, indeks):
        """Setter pocetka umjeravanja, integer"""
        if isinstance(indeks, QtCore.QModelIndex):
            n = int(indeks.row()) #redni broj indeksa
        else:
            n = indeks
        self.translatiraj_tocke(n)
        self.startIndeks = n
        self.endIndeks = max([max(i.indeksi) for i in self.tocke])
        self.layoutChanged.emit()

    def get_start(self):
        """getter pocetnog indeksa umjeravanja"""
        return self.startIndeks

    def get_kraj(self):
        """getter zavrsnog indeksa umjeravanja"""
        return self.endIndeks

    def get_startUmjeravanja(self):
        """getter pocetnog timestampa umjeravanja"""
        return self.dataFrejm.index[self.startIndeks]

    def get_krajUmjeravanja(self):
        """getter zavrsnog timestampa umjeravanja"""
        return self.dataFrejm.index[self.endIndeks]

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        definira broj redaka
        """
        return len(self.dataFrejm)

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        definira broj stupaca
        """
        return len(self.dataFrejm.columns)

    def flags(self, index):
        """
        definira ponasanje elemenata za pojedini indeks
        """
        if index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        """
        vraca vrijednost za svaki validni indeks i ulogu(display, background...)
        """
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        if role == QtCore.Qt.DisplayRole:
            return round(float(self.dataFrejm.iloc[row, col]), 1)
        if role == QtCore.Qt.ToolTipRole:
            return str(self.dataFrejm.iloc[row, col])
        if role == QtCore.Qt.BackgroundColorRole:
            for tocka in self.tocke:
                if tocka.test_indeks_unutar_tocke(row):
                    return QtGui.QBrush(tocka.boja)
            if row == self.startIndeks:
                brush = QtGui.QBrush()
                brush.setColor(QtGui.QColor(0, 0, 0, 80))
                brush.setStyle(QtCore.Qt.FDiagPattern)
                return brush
            elif row > self.startIndeks and row <= self.endIndeks:
                brush = QtGui.QBrush()
                brush.setColor(QtGui.QColor(0, 0, 0, 80))
                brush.setStyle(QtCore.Qt.Dense6Pattern)
                return brush
            else:
                return QtGui.QBrush(QtGui.QColor(255, 255, 255, 255))

    def headerData(self, section, orientation, role):
        """
        definira izgled headera (okomitih i vertikalnih)
        """
        if orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                #return str(self.dataFrejm.index[section].time())
                return str(self.dataFrejm.index[section])
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return str(self.dataFrejm.columns[section])
################################################################################
################################################################################
class RiseFallModel(QtCore.QAbstractTableModel):
    def __init__(self, slajs=None, naziv=None, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        if slajs is None:
            slajs = pd.Series()
        self.set_slajs(slajs, naziv)

        self.high = 90.0
        self.low = 10.0

        self.CHECKABLE = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable
        self.DISABLED = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable
        self.SELECTABLE = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def set_high_limit(self, value):
        self.high = value
        self.layoutChanged.emit()

    def get_high_limit(self):
        return self.high

    def set_low_limit(self, value):
        self.low = value
        self.layoutChanged.emit()

    def get_low_limit(self):
        return self.low

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

    def set_slajs(self, series, name):
        self.slajs = series
        self.dataFrejm = self.expand_frejm(series, name)
        self.layoutChanged.emit()

    def get_slajs(self):
        return self.slajs

    def set_frejm(self, frejm):
        self.dataFrejm = frejm
        #rekonstruiraj inicijalni slajs podataka
        self.slajs = self.dataFrejm.iloc[:,2]
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
                #return str(self.dataFrejm.index[section].time())
                return str(self.dataFrejm.index[section])
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                if section == 2:
                    return str(self.dataFrejm.columns[section])
                else:
                    return ''
            if role == QtCore.Qt.DecorationRole:
                if section == 0:
                    return QtGui.QIcon('./app/view/icons/rise.png')
                elif section == 1:
                    return QtGui.QIcon('./app/view/icons/fall.png')
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
                return round(float(self.dataFrejm.iloc[row-1, col]), 1)

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
################################################################################
################################################################################
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
################################################################################
################################################################################
class BareFrameModel(QtCore.QAbstractTableModel):
    """
    Model za prikaz preuzetih podataka.
    """
    def __init__(self, frejm=None, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        if frejm is None:
            frejm = pd.DataFrame()
        self.set_frejm(frejm)

    def set_frejm(self, frejm):
        self.dataFrejm = frejm
        self.layoutChanged.emit()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.dataFrejm)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.dataFrejm.columns)

    def flags(self, index):
        if index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        if role == QtCore.Qt.DisplayRole:
            return round(float(self.dataFrejm.iloc[row, col]), 1)
        if role == QtCore.Qt.ToolTipRole:
            return str(self.dataFrejm.iloc[row, col])

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return str(self.dataFrejm.index[section].time())
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return str(self.dataFrejm.columns[section])
################################################################################
################################################################################