# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 14:41:14 2015

@author: DHMZ-Milic
"""
import logging
from PyQt4 import QtGui, QtCore
from app.model.konfig_klase import Tocka


class BaseTablicaTocaka(QtCore.QAbstractTableModel):
    """
    Base klasa za tablice koje se koriste u wizardu
    """
    def __init__(self, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        Nuzna metoda za rad klase
        -vraca informaciju o broju redaka display djelu
        """
        return len(self.tocke)

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        Nuzna metoda za rad klase
        -vraca informaciju o broju stupaca display djelu
        """
        return len(self.headeri)

    def headerData(self, section, orientation, role):
        """
        Metoda postavlja headere u tablicu
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.headeri[section]
            else:
                return section


class Tablica1(BaseTablicaTocaka):
    """
    Prva tablica za definiranje tocaka. DOzvoljeno je mjenjanje naziva tocke i
    zavrsnog indeksa. Pocetni indeks se automatski definira kao zavrsni indeks
    prethodne tocke.
    """
    def __init__(self, tocke=None, parent=None):
        BaseTablicaTocaka.__init__(self, parent=parent)
        self.headeri = ['naziv',
                        'pocetni indeks',
                        'zavrsni indeks']
        if tocke == None:
            self.tocke = []
        else:
            self.tocke = tocke

    def flags(self, index):
        """metoda definira postavke pojedinih indeksa (editable, selectable...)"""
        col = index.column()
        if col in [0, 2]:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

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
                self.tocke[row].set_ime(value)
                return True
            elif col == 2:
                self.tocke[row].set_end(value)
                if row < self.rowCount()-1:
                    self.tocke[row+1].set_start(value)
                return True
            else:
                return False
        else:
            return False

    def data(self, index, role):
        """
        Za svaki role i indeks u tablici daje display djelu trazene vrijednosti
        """
        if not index.isValid():
            return None
        row = index.row()
        column = index.column()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if column == 0:
                value = self.tocke[row].ime
            elif column == 1:
                value = self.tocke[row].startIndeks
            elif column == 2:
                value = self.tocke[row].endIndeks
            return value


class Tablica2(BaseTablicaTocaka):
    """
    Druga tablica za definiranje tocaka. Slicna je prvoj tablici, ali dodan je
    novi stupac za definiranje broja zanemarenih indeksa. Jedino taj stupac
    je moguce mjenjati.
    """
    def __init__(self, tocke=None, parent=None):
        BaseTablicaTocaka.__init__(self, parent=parent)
        self.headeri = ['naziv',
                        'pocetni indeks',
                        'zavrsni indeks',
                        'broj zanemarenih']
        if tocke == None:
            self.tocke = []
        else:
            self.tocke = tocke

    def flags(self, index):
        """metoda definira postavke pojedinih indeksa (editable, selectable...)"""
        col = index.column()
        if col == 3:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """
        Metoda zaduzena za postavljanje novih vrijednosti u model(editable).
        """
        if not index.isValid():
            return False

        if role == QtCore.Qt.EditRole:
            row = index.row()
            col = index.column()
            if col == 3:
                self.tocke[row].set_zanemareni(value)
                return True
            else:
                return False
        else:
            return False

    def data(self, index, role):
        """
        Za svaki role i indeks u tablici daje display djelu trazene vrijednosti
        """
        if not index.isValid():
            return None
        row = index.row()
        column = index.column()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if column == 0:
                value = self.tocke[row].ime
            elif column == 1:
                value = self.tocke[row].startIndeks
            elif column == 2:
                value = self.tocke[row].endIndeks
            elif column == 3:
                value = self.tocke[row].brojZanemarenih
            return value


class Tablica3(BaseTablicaTocaka):
    """
    Treca tablica za definiranje tocaka. Slicna je drugoj tablici, ali dodan
    je stupac 'cref faktor' i njegove se vrijednosti jedino mogu mjenjati.
    """
    def __init__(self, tocke=None, parent=None):
        BaseTablicaTocaka.__init__(self, parent=parent)
        self.headeri = ['naziv',
                        'pocetni indeks',
                        'zavrsni indeks',
                        'broj zanemarenih',
                        'cref faktor']
        if tocke == None:
            self.tocke = []
        else:
            self.tocke = tocke

    def flags(self, index):
        """metoda definira postavke pojedinih indeksa (editable, selectable...)"""
        col = index.column()
        if col == 4:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """
        Metoda zaduzena za postavljanje novih vrijednosti u model(editable).
        """
        if not index.isValid():
            return False

        if role == QtCore.Qt.EditRole:
            row = index.row()
            col = index.column()
            if col == 4:
                self.tocke[row].set_crefFaktor(value)
                return True
            else:
                return False
        else:
            return False

    def data(self, index, role):
        """
        Za svaki role i indeks u tablici daje display djelu trazene vrijednosti
        """
        if not index.isValid():
            return None
        row = index.row()
        column = index.column()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if column == 0:
                value = self.tocke[row].ime
            elif column == 1:
                value = self.tocke[row].startIndeks
            elif column == 2:
                value = self.tocke[row].endIndeks
            elif column == 3:
                value = self.tocke[row].brojZanemarenih
            elif column == 4:
                value = self.tocke[row].crefFaktor
            return value


class Tablica4(Tablica3):
    """
    Verzija tablice 3, ali samo display, nema mogucnosti editiranja.
    """
    def __init__(self, tocke=None, parent=None):
        Tablica3.__init__(self, tocke=tocke, parent=parent)

    def flags(self, index):
        """metoda definira postavke pojedinih indeksa, samo display"""
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable



class CarobnjakZaDefiniranjeTocaka(QtGui.QWizard):
    """
    Wizard dijalog za definiranje postavki tocaka umjeravanja
    """
    def __init__(self, parent=None):
        logging.info('Pocetak inicijalizacije wizarda za definiranje tocaka.')
        QtGui.QWizard.__init__(self, parent)
        self.tocke = []
        self.zero = 1  # indeks pod kojim se nalazi zero
        self.span = 0  # indeks pod koim se nalazi span
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setMinimumSize(600,600)
        self.setWindowTitle("Read config file wizard")
        self.setOption(QtGui.QWizard.IndependentPages, on=False)
        self.P1 = PageBrojTocaka(parent=self)
        self.P2 = PageKranjiIndeksi(parent=self)
        self.P3 = PageBrojZanemarenih(parent=self)
        self.P4 = PageCref(parent=self)
        self.P5 = PageZero(parent=self)
        self.P6 = PageSpan(parent=self)
        self.setPage(1, self.P1)
        self.setPage(2, self.P2)
        self.setPage(3, self.P3)
        self.setPage(4, self.P4)
        self.setPage(5, self.P5)
        self.setPage(6, self.P6)
        self.setStartId(1)
        logging.info('Kraj inicijalizacije wizarda za definiranje tocaka.')

    def get_tocke(self):
        """Metoda vraca listu tocaka"""
        msg = 'tocke={0}'.format(self.tocke)
        logging.debug(msg)
        self.zero = self.P5.zeroIzbor
        self.span = self.P6.spanIzbor
        return self.tocke, self.zero, self.span


class PageBrojTocaka(QtGui.QWizardPage):
    """
    Stranice wizarda koja definira broj tocaka za umjeravanje.
    Sastoji se od labela i spinBox widgeta za izbor i promjenu broja tocaka.
    """
    def __init__(self, parent = None):
        QtGui.QWizard.__init__(self, parent)
        msg = 'Pocetak inicijalizacije stranice wizarda za broj tocaka'
        logging.debug(msg)
        self.setTitle('Izaberi broj umjernih tocaka')
        self.setSubTitle('Izaberi ukupni broj tocaka za umjeravanje. Mora se zadati vise od dvije tocke.')
        self.labelBrojTocaka = QtGui.QLabel('Broj umjernih tocaka :')
        self.spinBoxBrojTocaka = QtGui.QSpinBox()
        self.spinBoxBrojTocaka.setMinimum(2)
        self.spinBoxBrojTocaka.setMaximum(100)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.labelBrojTocaka)
        layout.addWidget(self.spinBoxBrojTocaka)
        self.setLayout(layout)
        self.spinBoxBrojTocaka.valueChanged.connect(self.promjeni_broj_tocaka)
        msg = 'Kraj inicijalizacije stranice wizarda za broj tocaka'
        logging.debug(msg)

    def promjeni_broj_tocaka(self, x):
        tocke = []
        for i in range(x):
            ime='TOCKA'+str(i+1)
            tocke.append(Tocka(ime=ime))
        self.wizard().tocke = tocke
        msg = 'Promjenjen broj umjernih tocaka, N={0}'.format(x)
        logging.debug(msg)

    def initializePage(self):
        self.promjeni_broj_tocaka(2)


class PageKranjiIndeksi(QtGui.QWizardPage):
    """
    Stranica wizarda koja omogucava promjenu naziva tocke i krajnjeg indeksa.
    Stranica se sastoji od tableView widgeta sa informacijama o tockama.
    """
    def __init__(self, parent = None):
        QtGui.QWizard.__init__(self, parent)
        msg = 'Pocetak inicijalizacije stranice wizarda za definiranje naziva i kranjih indeksa'
        logging.debug(msg)
        self.setTitle('Definiranje intervala indeksa za pojedinu tocku.')
        msg = 'Za svaku tocku odredite kranji indeks i naziv. Krajni indeksi moraju monotono rasti, moraju biti veci od 0 i moraju biti razliciti. Pocetni indeksi se automatski postavljaju prema zavrsnom indeksu prethodne tocke.'
        self.setSubTitle(msg)
        self.partialTable1 = QtGui.QTableView(parent=self)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.partialTable1)
        self.setLayout(layout)
        msg = 'Kraj inicijalizacije stranice wizarda za definiranje naziva i kranjih indeksa'
        logging.debug(msg)

    def initializePage(self):
        self.partialModel1 = Tablica1(tocke=self.wizard().tocke)
        self.partialTable1.setModel(self.partialModel1)
        self.partialTable1.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    def validatePage(self):
        krajevi = [tocka.endIndeks for tocka in self.wizard().tocke]
        sortiraniKrajevi = sorted(krajevi)
        setKrajeva = set(sortiraniKrajevi)
        veciOdNule = [value for value in krajevi if value >= 1]
        nazivi = [tocka.ime for tocka in self.wizard().tocke]
        if len(nazivi) != len(set(nazivi)):
            msg = 'Tocke moraju imati razlicite nazive.'
            QtGui.QMessageBox.warning(self, 'Problem', msg)
            return False
        if len(veciOdNule) != len(krajevi):
            msg = 'Jedan ili vise zavrsnih indeksa je negativan ili jednak nuli.'
            QtGui.QMessageBox.warning(self, 'Problem', msg)
            return False
        if krajevi != sortiraniKrajevi:
            msg = 'Vrijednost zavrsnih indeksa se ne povecava'
            QtGui.QMessageBox.warning(self, 'Problem', msg)
            return False
        if len(setKrajeva) != len(sortiraniKrajevi):
            msg = 'Neka vrijednost zavrsnog indeksa se ponavlja.'
            QtGui.QMessageBox.warning(self, 'Problem', msg)
            return False
        return True


class PageBrojZanemarenih(QtGui.QWizardPage):
    """
    Stranica wizarda za definiranje broja zanemarenih indeksa.
    Stranica se sastoji od tableView widgeta sa informacijama o tockama.
    """
    def __init__(self, parent = None):
        QtGui.QWizard.__init__(self, parent)
        msg = 'Pocetak inicijalizacije stranice wizarda za definiranje broja zanemarenih podataka'
        logging.debug(msg)
        self.setTitle('Definiranje broja zanemarenih podataka sa pocetka intervala za pojedinu tocku.')
        msg = 'Za svaku tocku odredi broj zanemarenih indeksa. Ukupan broj preostalih indeksa mora biti veci ili jednak 2.'
        self.setSubTitle(msg)
        self.partialTable2 = QtGui.QTableView(parent=self)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.partialTable2)
        self.setLayout(layout)
        msg = 'Kraj inicijalizacije stranice wizarda za definiranje broja zanemarenih podataka'
        logging.debug(msg)

    def initializePage(self):
        self.partialModel2 = Tablica2(tocke=self.wizard().tocke)
        self.partialTable2.setModel(self.partialModel2)
        self.partialTable2.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    def validatePage(self):
        t = [tocka.brojZanemarenih >= 0 for tocka in self.wizard().tocke]
        if False in t:
            msg = 'Barem jedna od vrijednosti broja zanemarenih je negativna.'
            QtGui.QMessageBox.warning(self, 'Problem', msg)
            return False
        n = [self._razmak(tocka) >= 2 for tocka in self.wizard().tocke]
        if False in n:
            msg = 'Barem jedna od tocaka nema dovoljan broj podataka (potrebno barem 2 indeksa)'
            QtGui.QMessageBox.warning(self, 'Problem', msg)
            return False
        return True

    def _razmak(self, tocka):
        return (tocka.endIndeks - tocka.startIndeks - tocka.brojZanemarenih)


class PageCref(QtGui.QWizardPage):
    """
    Stranica wizarda za definiranje cref faktora.
    Stranica se sastoji od tableView widgeta sa informacijama o tockama.
    """
    def __init__(self, parent = None):
        QtGui.QWizard.__init__(self, parent)
        msg = 'Pocetak inicijalizacije stranice wizarda za definiranje cref faktora'
        logging.debug(msg)
        self.setTitle('Definiranje Cref faktora za pojedinu tocku.')
        msg = 'Odradi cref faktor za tocke. Faktor mora biti broj unutar intervala [0, 1]. Barem jedan faktor mora biti nula (Zero) i barem jedan faktor mora biti veci od nule (Span).'
        self.setSubTitle(msg)
        self.partialTable3 = QtGui.QTableView(parent=self)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.partialTable3)
        self.setLayout(layout)
        msg = 'Kraj inicijalizacije stranice wizarda za definiranje cref faktora'
        logging.debug(msg)

    def initializePage(self):
        self.partialModel3 = Tablica3(tocke=self.wizard().tocke)
        self.partialTable3.setModel(self.partialModel3)
        self.partialTable3.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    def validatePage(self):
        cref = [tocka.crefFaktor for tocka in self.wizard().tocke]
        provjeraIntervala = [tocka >= 0 and tocka <= 1for tocka in cref]
        if False in provjeraIntervala:
            msg = 'Barem jedan cref faktor nije unutar intervala [0, 1].'
            QtGui.QMessageBox.warning(self, 'Problem', msg)
            return False
        if 0 not in cref:
            msg = 'Nedostaje cref faktor sa vrijednosti 0 (Zero).'
            QtGui.QMessageBox.warning(self, 'Problem', msg)
            return False
        if sum(cref) == 0:
            msg = 'Nedostaje cref faktor veci od nule (Span).'
            QtGui.QMessageBox.warning(self, 'Problem', msg)
            return False
        return True

class PageZero(QtGui.QWizardPage):
    """
    Stranica wizarda za izbor zero tocke. Stranica se sastoji od tableView
    widgeta sa informacijama o tockama.
    """
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        msg = 'Pocetak inicijalizacije stranice wizarda za definiranje zero tocke'
        logging.debug(msg)
        self.setTitle('Odeberite ZERO tocku')
        msg = 'Izaberite zero tocku klikom na tablicu. Zero tocka mora imati cref faktor jednak 0.'
        self.setSubTitle(msg)
        self.partialTable4 = QtGui.QTableView(parent=self)
        self.partialTable4.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.partialTable4.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.partialTable4)
        self.setLayout(layout)
        self.partialTable4.clicked.connect(self.select_zero)
        self.zeroIzbor = None

        msg = 'Kraj inicijalizacije stranice wizarda za definiraje zero tocke'
        logging.debug(msg)

    def select_zero(self, x):
        """
        Izbor zero tocke iz tablice, ovisno o izabranom redu, zapamit tocku
        """
        red = x.row()
        self.zeroIzbor = self.wizard().tocke[red]

    def initializePage(self):
        self.partialModel4 = Tablica4(tocke=self.wizard().tocke)
        self.partialTable4.setModel(self.partialModel4)
        self.partialTable4.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    def validatePage(self):
        if self.zeroIzbor is None:
            msg = 'Niste izabrali tocku u tablici.'
            QtGui.QMessageBox.warning(self, 'Problem', msg)
            return False
        if float(self.zeroIzbor.crefFaktor) != 0.0:
            msg = 'Izabrana tocka ne moze biti ZERO, cref faktor tocke nije jednak 0.'
            QtGui.QMessageBox.warning(self, 'Problem', msg)
            return False
        return True


class PageSpan(QtGui.QWizardPage):
    """
    Stranica wizarda za izbor Span tocke. Stranica se sastoji od tableView
    widgeta sa informacijama o tockama.
    """
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        msg = 'Pocetak inicijalizacije stranice wizarda za definiranje span tocke'
        logging.debug(msg)
        self.setTitle('Odeberite SPAN tocku')
        msg = 'Izaberite span tocku klikom na tablicu. Span tocka mora imati cref faktor veci od 0.'
        self.setSubTitle(msg)
        self.partialTable5 = QtGui.QTableView(parent=self)
        self.partialTable5.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.partialTable5.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.partialTable5)
        self.setLayout(layout)
        self.partialTable5.clicked.connect(self.select_span)
        self.spanIzbor = None

        msg = 'Kraj inicijalizacije stranice wizarda za definiraje span tocke'
        logging.debug(msg)

    def select_span(self, x):
        """
        Izbor zero tocke iz tablice, ovisno o izabranom redu, zapamit tocku
        """
        red = x.row()
        self.spanIzbor = self.wizard().tocke[red]

    def initializePage(self):
        self.partialModel5 = Tablica4(tocke=self.wizard().tocke)
        self.partialTable5.setModel(self.partialModel5)
        self.partialTable5.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    def validatePage(self):
        if self.spanIzbor is None:
            msg = 'Niste izabrali tocku u tablici.'
            QtGui.QMessageBox.warning(self, 'Problem', msg)
            return False
        if float(self.spanIzbor.crefFaktor) is 0.0:
            msg = 'Izabrana tocka ne moze biti SPAN, cref faktor ne smije biti 0.'
            QtGui.QMessageBox.warning(self, 'Problem', msg)
            return False
        return True
