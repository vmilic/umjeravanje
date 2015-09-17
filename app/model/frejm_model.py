# -*- coding: utf-8 -*-
"""
Created on Mon May 18 13:53:03 2015

@author: DHMZ-Milic
"""
import pandas as pd
import numpy as np
from PyQt4 import QtCore, QtGui

class RichTextDelegate(QtGui.QStyledItemDelegate):
    """
    Ideja preuzeta sa:
    http://stackoverflow.com/questions/2959850/how-to-make-item-view-render-rich-html-text-in-pyqt?rq=1
    """
    def __init__(self, parent=None):
        QtGui.QStyledItemDelegate.__init__(self, parent=parent)

    def paint(self, painter, option, index):
        tekst = index.data(role=QtCore.Qt.DisplayRole)
        doc = QtGui.QTextDocument(self)
        doc.setHtml(tekst)
        doc.setTextWidth(option.rect.width())
        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()
        painter.save()
        #brush setting setBrush color...
        #painter.setBackgroundMode(QtCore.Qt.OpaqueMode)
        red = index.row()
        testzaboju = index.model().lista[red][4]
        #TODO! problem kod selektiranja... ovarloadao sam paint metodu pa se ne iscrtava selection.
        if option.state & QtGui.QStyle.State_Selected:
            #TODO! trebam naci istu nijansu boje za select
            #TODO! trebam prebaciti boju za tekst u bijelu
            painter.fillRect(option.rect, QtGui.QBrush(QtCore.Qt.blue))
            painter.setPen(QtGui.QPen(QtCore.Qt.white))
        else:
            if testzaboju:
                painter.fillRect(option.rect, QtGui.QBrush(QtGui.QColor(0, 255, 0, 90)))
                #painter.setBackground(QtGui.QBrush(QtGui.QColor(0, 255, 0, 90)))
            else:
                painter.fillRect(option.rect, QtGui.QBrush(QtGui.QColor(255, 0, 0, 90)))
                #painter.setBackground(QtGui.QBrush(QtGui.QColor(255, 0, 0, 90)))
        painter.translate(option.rect.topLeft());
        painter.setClipRect(option.rect.translated(-option.rect.topLeft()))
        dl = doc.documentLayout()
        dl.draw(painter, ctx)
        painter.restore()


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

    def set_start_prilikom_loada(self, indeks):
        """
        metoda sluzi da se postavi pocetak umjeravanja prilikom loadanja iz
        spremljenog filea. Problem nastaje jer se indeksi u tockama ne smiju
        pomicati...
        """
        if isinstance(indeks, QtCore.QModelIndex):
            n = int(indeks.row()) #redni broj indeksa
        else:
            n = indeks
        self.startIndeks = n
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

    def set_start_prilikom_loada(self, indeks):
        """
        metoda sluzi da se postavi pocetak umjeravanja prilikom loadanja iz
        spremljenog filea. Problem nastaje jer se indeksi u tockama ne smiju
        pomicati...
        """
        if isinstance(indeks, QtCore.QModelIndex):
            n = int(indeks.row()) #redni broj indeksa
        else:
            n = indeks
        self.startIndeks = n
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
        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter
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

class KonverterRezultatModel(QtCore.QAbstractTableModel):
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
        self.jedinica = 'n/a'

    def set_mjerna_jedinica(self, jedinica):
        """
        setter mjerne jedinice
        """
        self.jedinica = str(jedinica)
        self.layoutChanged.emit()

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
        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter
        if role == QtCore.Qt.ToolTipRole:
            return str(self.dataFrejm.iloc[row, col])
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            value = self.dataFrejm.iloc[row, col]
            if np.isnan(value) and col >= 1:
                return '' #ne prikazuj nan vrijednosti za sve osim cref
            if not isinstance(value, str):
                value = round(value, 1)
            # zero tocka ima apsolutno odstupanje, dodaj mjernu jedinicu
            if col == 5 and  self.dataFrejm.iloc[row, 0] == 0:
                value = " ".join([str(value), self.jedinica])
            return str(value)
        if role == QtCore.Qt.BackgroundColorRole:
            return self.tocke[row].boja

    def headerData(self, section, orientation, role):
        """
        Sets the headers of the table...
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Vertical:
                return str(section+1)
                    #return str(self.dataFrejm.index[section])
            elif orientation == QtCore.Qt.Horizontal:
                # display mjernih jedinica u headerima
                value = str(self.dataFrejm.columns[section])
                mj = "".join(['\n', '(', self.jedinica, ')'])
                out = " ".join([value, mj])
                return out


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

class EfikasnostKonverteraModel(QtCore.QAbstractTableModel):
    """
    Model za prikaz podataka sa slope, offset, prilagodba A i prilagodba B
    """
    def __init__(self, lista=None, parent=None):
        """
        Initialize with pandas dataframe
        """
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.indeksi = ['Ec1', 'Ec2', 'Ec3', 'Ec']
        self.set_lista(lista)
        self.jedinica = '(%)'

    def set_mjerna_jedinica(self, jedinica):
        """
        setter mjerne jedinice
        """
        self.jedinica = "".join(['(', str(jedinica), ')'])
        self.layoutChanged.emit()

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
        return 4

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        MUST BE IMPLEMENTED
        Return number of columns of pandas dataframe. (add one for time index)
        """
        return 1

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
        if role == QtCore.Qt.ToolTipRole:
            return str(self.lista[row])
        if role == QtCore.Qt.DisplayRole:
            value = self.lista[row]
            if not isinstance(value, str):
                value = round(value, 3)
            return str(value)

    def headerData(self, section, orientation, role):
        """
        Sets the headers of the table...
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                out = "".join(['Efikasnost\n', self.jedinica])
                return out
            elif orientation == QtCore.Qt.Vertical:
                value = self.indeksi[section]
                return str(value)
