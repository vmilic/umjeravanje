# -*- coding: utf-8 -*-
"""
Created on Mon May 18 13:53:03 2015

@author: DHMZ-Milic
"""
import logging
import pandas as pd
from PyQt4 import QtCore, QtGui


class WorkingFrameModel(QtCore.QAbstractTableModel):
    """
    Model 3 minutno agregiranih podataka za umjeravanje.
    """
    def __init__(self, frejm=pd.DataFrame(), cfg=None, parent=None):
        """Initialize with pandas dataframe"""
        logging.debug('Start inicijalizacije WorkingFrameModel')
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.dataFrejm = frejm
        self.cfg = cfg
        logging.debug('Kraj inicijalizacije WorkingFrameModel')

    def set_frejm(self, frejm):
        """seter za podatke"""
        self.dataFrejm = frejm
        msg = 'Novi frejm postavljen:\n{0}'.format(str(frejm))
        logging.debug(msg)
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
            tocke = self.cfg.umjerneTocke
            tockeColor1 = [i for i in tocke if tocke.index(i)%2 == 0]
            tockeColor2 = [i for i in tocke if tocke.index(i)%2 != 0]
            for tocka in tockeColor1:
                if tocka.index_is_member(row):
                    return QtGui.QBrush(QtGui.QColor(0, 150, 220, 80))
            for tocka in tockeColor2:
                if tocka.index_is_member(row):
                    return QtGui.QBrush(QtGui.QColor(0, 25, 220, 80))

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


class KonverterAvgFrameModel(WorkingFrameModel):
    """
    model agregiranih podataka za racunanje provjere konvertera.
    """
    def __init__(self, frejm=pd.DataFrame(), cfg=None, parent=None):
        WorkingFrameModel.__init__(self, frejm=frejm, cfg=cfg, parent=parent)

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
            # obojaj pozadinu reda ovisno o kojoj tocki pripada
            if self.cfg.Ktocka1.index_is_member(row):
                return QtGui.QBrush(QtGui.QColor(0, 150, 220, 80))
            elif self.cfg.Ktocka2.index_is_member(row):
                return QtGui.QBrush(QtGui.QColor(0, 25, 220, 80))
            elif self.cfg.Ktocka3.index_is_member(row):
                return QtGui.QBrush(QtGui.QColor(0, 150, 220, 80))
            elif self.cfg.Ktocka4.index_is_member(row):
                return QtGui.QBrush(QtGui.QColor(0, 25, 220, 80))
            elif self.cfg.Ktocka5.index_is_member(row):
                return QtGui.QBrush(QtGui.QColor(0, 150, 220, 80))
            elif self.cfg.Ktocka6.index_is_member(row):
                return QtGui.QBrush(QtGui.QColor(0, 25, 220, 80))



class SiroviFrameModel(QtCore.QAbstractTableModel):
    """
    Model sa sirovim podacima za umjeravanje
    """
    def __init__(self, frejm=pd.DataFrame(), parent=None):
        """Initialize with pandas dataframe"""
        logging.debug('Start inicijalizacije SiroviFrameModel')
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.dataFrejm = frejm
        self.startIndeks = None
        self.endIndeks = None
        logging.debug('Kraj inicijalizacije SiroviFrameModel')

    def set_frejm(self, frejm):
        """
        seter za podatke
        """
        self.dataFrejm = frejm
        msg = 'Novi frejm postavljen:\n{0}'.format(str(frejm))
        logging.debug(msg)
        self.layoutChanged.emit()

    def set_slajs_len(self, red, duljina):
        """
        setter za broj podataka unutar izabranog slajsa.
        Samo radi vizualnog prikaza u tablici
        """
        self.startIndeks = red
        self.endIndeks = red+duljina
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
            # obojaj pozadinu ovisno o izabranoj tocki (redu)
            if self.startIndeks is not None and self.endIndeks is not None:
                if index.row() >= self.startIndeks and index.row() < self.endIndeks:
                    return QtGui.QBrush(QtGui.QColor(0, 25, 220, 80))
                else:
                    return QtGui.QBrush(QtGui.QColor(255, 255, 255, 255))
            else:
                return QtGui.QBrush(QtGui.QColor(255, 255, 255, 255))

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


class RezultatModel(QtCore.QAbstractTableModel):
    """
    Model tablica za rezultate umjeeravanja
    """
    def __init__(self, frejm=pd.DataFrame(), parent=None):
        """
        Initialize with pandas dataframe
        """
        logging.debug('Start inicijalizacije RezultatModel')
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.dataFrejm = frejm
        logging.debug('Kraj inicijalizacije RezultatModel')

    def set_frejm(self, frejm):
        """
        seter za podatke
        """
        self.dataFrejm = frejm
        msg = 'Novi frejm postavljen:\n{0}'.format(str(frejm))
        logging.debug(msg)
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
