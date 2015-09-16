# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 10:40:16 2015

@author: DHMZ-Milic
"""
from PyQt4 import QtGui, QtCore
import numpy as np
import pandas as pd


#class TableViewRezultata(QtGui.QTableView):
#    """
#    view za rezultate umjeravanja po tockama. podrska za kontekstni menu
#    """
#    def __init__(self, parent=None):
#        QtGui.QTableView.__init__(self, parent=parent)
#        #self.verticalHeader().setVisible(False)
#        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
#        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
#        self.setMinimumSize(535,210)
#        self.setMaximumSize(535,210)
#
#    def reset_column_widths(self):
#        """
#        metoda resizea tablicu
#        """
#        self.setWordWrap(True)
#        self.horizontalHeader().setStretchLastSection(True)
#        self.horizontalHeader().resizeSection(0,80)
#        self.horizontalHeader().resizeSection(1,80)
#        self.horizontalHeader().resizeSection(2,80)
#        self.horizontalHeader().resizeSection(3,80)
#
#    def contextMenuEvent(self, event):
#        """
#        event koji definira kontekstni menu..
#        """
#        self.selected = self.selectionModel().selection().indexes()
#        #define context menu items
#        menu = QtGui.QMenu()
#        dodaj = QtGui.QAction('Dodaj tocku', self)
#        makni = QtGui.QAction('Makni tocku', self)
#        postavke = QtGui.QAction('Postavke tocke', self)
#        menu.addAction(dodaj)
#        menu.addAction(makni)
#        menu.addSeparator()
#        menu.addAction(postavke)
#        #connect context menu items
#        dodaj.triggered.connect(self.emit_add)
#        makni.triggered.connect(self.emit_remove)
#        postavke.triggered.connect(self.emit_edit)
#        #display context menu
#        menu.exec_(self.mapToGlobal(event.pos()))
#
#    def emit_add(self, x):
#        """
#        Metoda emitira zahtjev za dodavanjem nove tocke
#        """
#        #za sada nemam pametniju ideju
#        if len(self.model().dataFrejm):
#            self.emit(QtCore.SIGNAL('dodaj_tocku'))
#
#    def emit_remove(self, x):
#        """
#        Metoda emitira zahtjev za brisanjem tocke
#        """
#        selektirani = self.selectedIndexes()
#        if selektirani:
#            indeks = selektirani[0].row()
#            self.emit(QtCore.SIGNAL('makni_tocku(PyQt_PyObject)'), indeks)
#
#    def emit_edit(self, x):
#        """
#        Metoda salje zahtjev za promjenom parametara selektirane tocke
#        """
#        selektirani = self.selectedIndexes()
#        if selektirani:
#            indeks = selektirani[0].row()
#            self.emit(QtCore.SIGNAL('edit_tocku(PyQt_PyObject)'), indeks)


class TableViewRezultataKonvertera(QtGui.QTableView):
    """
    view za rezultate provjere konvertera.
    """
    def __init__(self, parent=None):
        QtGui.QTableView.__init__(self, parent=parent)
        self.setMinimumSize(355,220)
        self.setMaximumSize(355,220)

    def reset_column_widths(self):
        self.setWordWrap(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().resizeSection(0,80)
        self.horizontalHeader().resizeSection(1,80)
        self.horizontalHeader().resizeSection(2,80)


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


class TablicaUmjeravanjeKriterij(QtGui.QWidget):
    """
    Tablica za parametre umjeravanja, Srs, Srz, rz, rmax
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent=parent)
        self.setter_podataka = {'srs':self.set_srs_values,
                                'srz':self.set_srz_values,
                                'rz':self.set_rz_values,
                                'rmax':self.set_rmax_values}
        # definicija layouta
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setHorizontalSpacing(1)
        self.gridLayout.setVerticalSpacing(1)
        self.gridLayout.setContentsMargins(0,0,0,0)
        # definicija labela unutar tablice
        # red 0 i granice
        self.pos00 = CustomLabel(tekst='')
        self.pos01 = CustomLabel(tekst='<b> Naziv kriterija </b>', center=True)
        self.pos02 = CustomLabel(tekst='<b> Rezultati </b>', center=True)
        self.pos03 = CustomLabel(tekst='')
        self.pos04 = CustomLabel(tekst='<b> Uvijet prihvatljivosti </b>', center=True)
        self.pos05 = CustomLabel(tekst='<b> Ispunjeno </b>', center=True)
        self.pos10 = CustomLabel(tekst='<b> 1 </b>', center=True)
        self.pos20 = CustomLabel(tekst='<b> 2 </b>', center=True)
        self.pos30 = CustomLabel(tekst='<b> 3 </b>', center=True)
        self.pos40 = CustomLabel(tekst='<b> 4 </b>', center=True)
        #red 1
        self.pos11 = CustomLabel(tekst=' Ponovljivost standardne devijacije u nuli ')
        self.pos12 = CustomLabel(tekst=' S<sub>r,z</sub> = ')
        self.pos13 = CustomLabel()
        self.pos14 = CustomLabel(center=True)
        self.pos15 = CustomLabel(tekst='Ne', center=True)
        self.red1 = [self.pos10, self.pos11, self.pos12, self.pos13, self.pos14, self.pos15]
        #red 2
        self.pos21 = CustomLabel(tekst=' Ponovljivost standardne devijacije pri koncentraciji ct ')
        self.pos22 = CustomLabel(tekst=' S<sub>r,ct</sub> = ')
        self.pos23 = CustomLabel()
        self.pos24 = CustomLabel(center=True)
        self.pos25 = CustomLabel(tekst='Ne', center=True)
        self.red2 = [self.pos20, self.pos21, self.pos22, self.pos23, self.pos24, self.pos25]
        #red 3
        self.pos31 = CustomLabel(tekst=' Odstupanje od linearnosti u nuli ')
        self.pos32 = CustomLabel(tekst=' r<sub>z</sub> = ')
        self.pos33 = CustomLabel()
        self.pos34 = CustomLabel(center=True)
        self.pos35 = CustomLabel(tekst='Ne', center=True)
        self.red3 = [self.pos30, self.pos31, self.pos32, self.pos33, self.pos34, self.pos35]
        #red 4
        self.pos41 = CustomLabel(tekst=' Maksimalno relativno odstupanje od linearnosti ')
        self.pos42 = CustomLabel(tekst=' r<sub>z,rel</sub> = ')
        self.pos43 = CustomLabel()
        self.pos44 = CustomLabel(center=True)
        self.pos45 = CustomLabel(tekst='Ne', center=True)
        self.red4 = [self.pos40, self.pos41, self.pos42, self.pos43, self.pos44, self.pos45]
        self.datarows = [self.red1, self.red2, self.red3, self.red4]
        #slaganje labela u grid layout...
        # self.gridLayout.addWidget(widget, row, col, rowspan, colspan)
        self.gridLayout.addWidget(self.pos00 ,0 ,0 ,1 ,1)
        self.gridLayout.addWidget(self.pos01 ,0 ,1 ,1 ,1)
        self.gridLayout.addWidget(self.pos02 ,0 ,2 ,1 ,2)
        self.gridLayout.addWidget(self.pos04 ,0 ,4 ,1 ,1)
        self.gridLayout.addWidget(self.pos05 ,0 ,5 ,1 ,1)
        self.gridLayout.addWidget(self.pos10 ,1 ,0 ,1 ,1)
        self.gridLayout.addWidget(self.pos20 ,2 ,0 ,1 ,1)
        self.gridLayout.addWidget(self.pos30 ,3 ,0 ,1 ,1)
        self.gridLayout.addWidget(self.pos40 ,4 ,0 ,1 ,1)
        for row, labelList in enumerate(self.datarows):
            for col, label in enumerate(self.datarows[row]):
                self.gridLayout.addWidget(label, row+1, col, 1, 1)
        #definiranje minimalne velicine stupaca
        for i in range(5):
            self.set_minimum_height_for_row(i, 30)
        self.set_minimum_width_for_column(0, 30)
        self.set_minimum_width_for_column(1, 200)
        self.set_minimum_width_for_column(2, 75)
        self.set_minimum_width_for_column(3, 75)
        self.set_minimum_width_for_column(4, 150)
        self.set_minimum_width_for_column(5, 75)

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
        if check == 'Da':
            color = QtGui.QColor(QtGui.QColor(0, 255, 0, 90))
        else:
            color = QtGui.QColor(QtGui.QColor(255, 0, 0, 90))
        return color

    def set_srz_values(self, values):
        """
        setter za srz
        """
        value, limit, check = values
        self.pos13.setText(value)
        self.pos14.setText(limit)
        self.pos15.setText(check)
        color = self.find_needed_color(check)
        self.set_row_background_color(1, color)

    def set_srs_values(self, values):
        """
        setter za srs
        """
        value, limit, check = values
        self.pos23.setText(value)
        self.pos24.setText(limit)
        self.pos25.setText(check)
        color = self.find_needed_color(check)
        self.set_row_background_color(2, color)

    def set_rz_values(self, values):
        """
        setter za rz
        """
        value, limit, check = values
        self.pos33.setText(value)
        self.pos34.setText(limit)
        self.pos35.setText(check)
        color = self.find_needed_color(check)
        self.set_row_background_color(3, color)

    def set_rmax_values(self, values):
        """
        setter za rmax
        """
        value, limit, check = values
        self.pos43.setText(value)
        self.pos44.setText(limit)
        self.pos45.setText(check)
        color = self.find_needed_color(check)
        self.set_row_background_color(4, color)

    def clear_results(self):
        """
        Clear rezultata tablice
        """
        #resert color
        for red in range(1, 5):
            self.set_row_background_color(red, QtGui.QColor(QtCore.Qt.white))
        #reset values
        self.pos13.setText('n/a')
        self.pos14.setText('n/a')
        self.pos15.setText('n/a')
        self.pos23.setText('n/a')
        self.pos24.setText('n/a')
        self.pos25.setText('n/a')
        self.pos33.setText('n/a')
        self.pos34.setText('n/a')
        self.pos35.setText('n/a')
        self.pos43.setText('n/a')
        self.pos44.setText('n/a')
        self.pos45.setText('n/a')

    def set_values(self, data):
        """
        setter vrijednosti u tablicu
        ulazni parametar je dictionary sa 4 kljuca: ('srs', 'srz', 'rz', 'rmax')
        pod svakim kljucem nalazi se lista od 3 stringa: [value, limit, check]
        """
        for (key, value) in data.items():
            try:
                s = self.setter_podataka[key]
                s(value)
            except LookupError:
                pass

    def set_row_background_color(self, rowNumber, color):
        """
        metoda za promjenu pozadinske boje reda u tablici
        ulazni parametar je broj reda (int) i boja (QColor)
        """
        if rowNumber in [1, 2, 3, 4]:
            red = self.datarows[rowNumber-1]
            for label in red:
                label.set_color(color)
        else:
            raise ValueError('Nije zadan valjani red')

    def hide_row(self, rowNumber, check):
        """
        metoda za sakrivanje reda u tablici (za potrebe provjere linearnosti)
        ulazni parametar je broj reda (int) i boolean koji odredjuje vidljivost
        (True --> visible, False --> hidden)
        """
        if rowNumber in [1, 2, 3, 4]:
            red = self.datarows[rowNumber-1]
            for label in red:
                label.setVisible(check)
        else:
            raise ValueError('Nije zadan valjani red')

    def toggle_linearnost(self, x):
        """
        metoda za skrivanje stupaca ako nije ukljucena provjera linearnosti
        """
        self.hide_row(3, x)
        self.hide_row(4, x)


class TablicaFunkcijePrilagodbe(QtGui.QWidget):
    """
    Tablica za prikaz parametara funkcije prilagodbe
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent=parent)

        self.naslov = CustomLabel(tekst=' <b>Funkcija prilagodbe</b> ', center=True)
        self.formula = CustomLabel(tekst=' C = A * Cm + B ', center=True)
        self.labelA = CustomLabel(tekst=' <b>A = </b> ')
        self.valueA = CustomLabel()
        self.labelB = CustomLabel(tekst=' <b>B = </b> ')
        self.valueB = CustomLabel()

        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setHorizontalSpacing(1)
        self.gridLayout.setVerticalSpacing(1)
        self.gridLayout.setContentsMargins(0,0,0,0)

        self.gridLayout.addWidget(self.naslov, 0, 0, 1, 4)
        self.gridLayout.addWidget(self.formula, 1, 0, 1, 4)
        self.gridLayout.addWidget(self.labelA, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.valueA, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.labelB, 2, 2, 1, 1)
        self.gridLayout.addWidget(self.valueB, 2, 3, 1, 1)

        for i in range(3):
            self.set_minimum_height_for_row(i, 30)
        for i in range(4):
            self.set_minimum_width_for_column(i, 50)

        self.setLayout(self.gridLayout)

    def set_minimum_width_for_column(self, col, size):
        self.gridLayout.setColumnMinimumWidth(col, size)

    def set_minimum_height_for_row(self, row, size):
        self.gridLayout.setRowMinimumHeight(row, size)

    def set_values(self, value):
        """setter vrijednosti value
        ulazni parametar value je lista sa dva elementa [A , B]"""
        a, b = value
        self.valueA.setText(a)
        self.valueB.setText(b)

    def reset_value(self):
        """
        reset vrijednosti parametara na 'n/a'
        """
        self.valueA.setText('n/a')
        self.valueB.setText('n/a')


class TablicaKonverterParametri(QtGui.QWidget):
    """
    tablica za prikaz efikasnosti konvertera
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent=parent)

        self.naslov = CustomLabel(tekst='<b> Efikasnost konvertera (%) </b>', center=True)
        self.n1 = CustomLabel(tekst=' <b>Ec1 = </b> ', center=True)
        self.n2 = CustomLabel(tekst=' <b>Ec2 = </b> ', center=True)
        self.n3 = CustomLabel(tekst=' <b>Ec3 = </b> ', center=True)
        self.n4 = CustomLabel(tekst=' <b>Ec = </b> ', center=True)

        self.valueEc1 = CustomLabel()
        self.valueEc2 = CustomLabel()
        self.valueEc3 = CustomLabel()
        self.valueEc = CustomLabel()

        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setHorizontalSpacing(1)
        self.gridLayout.setVerticalSpacing(1)
        self.gridLayout.setContentsMargins(0,0,0,0)

        self.gridLayout.addWidget(self.naslov, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.n1, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.n2, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.n3, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.n4, 4, 0, 1, 1)
        self.gridLayout.addWidget(self.valueEc1, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.valueEc2, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.valueEc3, 3, 1, 1, 1)
        self.gridLayout.addWidget(self.valueEc, 4, 1, 1, 1)

        self.gridLayout.addWidget(self.naslov, 0, 0, 1, 4)

        for i in range(5):
            self.set_minimum_height_for_row(i, 30)
        for i in range(2):
            self.set_minimum_width_for_column(i, 80)

        self.setLayout(self.gridLayout)

    def set_minimum_width_for_column(self, col, size):
        self.gridLayout.setColumnMinimumWidth(col, size)

    def set_minimum_height_for_row(self, row, size):
        self.gridLayout.setRowMinimumHeight(row, size)

    def set_values(self, value):
        """setter vrijednosti value
        ulazni parametar value je lista sa 4 elementa (str): [Ec1 , Ec2, Ec3, Ec]
        """
        e1, e2, e3, e = value
        self.valueEc1.setText(e1)
        self.valueEc2.setText(e2)
        self.valueEc3.setText(e3)
        self.valueEc.setText(e)

    def reset_value(self):
        """
        reset vrijednosti parametara na 'n/a'
        """
        self.valueEc1.setText('n/a')
        self.valueEc2.setText('n/a')
        self.valueEc3.setText('n/a')
        self.valueEc.setText('n/a')


class CustomLabelContext(CustomLabel):
    """
    custom label sa podrskom za kontekstni meni
    """
    def __init__(self, tekst='n/a', center=False, parent=None):
        CustomLabel.__init__(self, tekst=tekst, center=center, parent=parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)


class TablicaUmjeravanje(QtGui.QWidget):
    def __init__(self, tocke=None, data=None, jedinica=None, parent=None):
        """
        Widget sa tablicom za prikaz rezultata umjeravanja.

        inicijalizacija sa tockama umjeravanja, pandas datafrejmom sa rezultatima
        umjeravanja i stringom mjerne jedinice
        """
        QtGui.QWidget.__init__(self, parent=parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #bitni memberi
        self.tocke = tocke #tocke umjeravanja
        self.data = data #pandas datafrejm rezultata umjeravanja
        self.jedinica = jedinica #string mjerne jedinice
        assert self.tocke != None , 'Nisu zadane tocke umjeravanja'
        assert isinstance(self.data, pd.core.frame.DataFrame), 'Rezultati umjeravanja nisu pandas dataframe'
        assert self.jedinica != None , 'Nije zadana mjerna jedinica'
        assert len(self.tocke) == len(self.data), 'Broj tocaka ne odgovara broju rezultata'

        self.sastavi_tablicu()

        self.setLayout(self.gridLayout)

    def sastavi_tablicu(self):
        """
        sastavljanje output tablice.
        """
        #definiranje grid layouta
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setHorizontalSpacing(1)
        self.gridLayout.setVerticalSpacing(1)
        self.gridLayout.setContentsMargins(0,0,0,0)
        #headeri
        self.redniBroj = CustomLabelContext(tekst='#', center=True)
        self.redniBroj.customContextMenuRequested.connect(self.contextMenuEvent)
        t = "".join(['cref\n(', self.jedinica, ')'])
        self.cref = CustomLabelContext(tekst=t, center=True)
        #self.cref.customContextMenuRequested.connect(self.contextMenuEvent)
        self.U = CustomLabelContext(tekst='U\n(%)', center=True)
        #self.U.customContextMenuRequested.connect(self.contextMenuEvent)
        t = "".join(['c\n(', self.jedinica, ')'])
        self.c = CustomLabelContext(tekst='c', center=True)
        #self.c.customContextMenuRequested.connect(self.contextMenuEvent)
        t = "".join(['\u0394\n(', self.jedinica, ')'])
        self.delta = CustomLabelContext(tekst=t, center=True)
        #self.delta.customContextMenuRequested.connect(self.contextMenuEvent)
        t = "".join(['sr\n(', self.jedinica, ')'])
        self.sr = CustomLabelContext(tekst=t, center=True)
        #self.sr.customContextMenuRequested.connect(self.contextMenuEvent)
        self.r = CustomLabelContext(tekst='r\n(%)', center=True)
        #self.r.customContextMenuRequested.connect(self.contextMenuEvent)
        #dodavanje headera u layout
        self.gridLayout.addWidget(self.redniBroj, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.cref, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.U, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.c, 0, 3, 1, 1)
        self.gridLayout.addWidget(self.delta, 0, 4, 1, 1)
        self.gridLayout.addWidget(self.sr, 0, 5, 1, 1)
        self.gridLayout.addWidget(self.r, 0, 6, 1, 1)
        #podesavanje horizontalnih dimenzija labela u layoutu za pojedine stupce
        self.set_minimum_width_for_column(0, 30)
        self.set_minimum_width_for_column(1, 75)
        self.set_minimum_width_for_column(2, 75)
        self.set_minimum_width_for_column(3, 75)
        self.set_minimum_width_for_column(4, 75)
        self.set_minimum_width_for_column(5, 75)
        self.set_minimum_width_for_column(6, 75)
        #dodavanje labela sa rezultatima u layout
        for i in range(len(self.tocke)):
            #TODO!
            self.set_minimum_height_for_row(i+1, 30)
            tocka = self.tocke[i]
            for j in range(7):
                #zapis rednog broja podatka
                if j == 0:
                    txt = str(i+1)
                else:
                    podatak = self.data.iloc[i, j-1] #trazeni element u frejmu
                    podatak = round(podatak, 2)
                    if np.isnan(podatak):
                        #nan slucaj
                        txt = ""
                    elif j == 6 and self.data.iloc[i, 0] == 0:
                        #zero slucaj kod racunanja r
                        txt = " ".join([str(podatak), self.jedinica])
                    else:
                        #normalni slucaj
                        txt = str(podatak)
                lab = CustomLabelContext(tekst=txt)
                #connect signal za custom menu
                lab.customContextMenuRequested.connect(self.contextMenuEvent)
                #boja
                lab.set_color(tocka.boja)
                #postavljanje labela u layout
                self.gridLayout.addWidget(lab, i+1, j, 1, 1)

    def set_minimum_width_for_column(self, col, size):
        """
        odredjivanje minimalne sirine stupca
        """
        self.gridLayout.setColumnMinimumWidth(col, size)

    def set_minimum_height_for_row(self, row, size):
        """
        odredjivanje minimalne visine redka
        """
        self.gridLayout.setRowMinimumHeight(row, size)

    def contextMenuEvent(self, position):
        """
        Prikaz kontekstnog menija
        """
        snd = self.sender()
        self.redak, self.stupac = self.find_location_of_sender(snd)
        menu = QtGui.QMenu()
        dodaj = QtGui.QAction('Dodaj tocku', self)
        makni = QtGui.QAction('Makni tocku', self)
        postavke = QtGui.QAction('Postavke tocke', self)
        nred = self.gridLayout.rowCount()
        if nred > 3:
            menu.addAction(dodaj)
            menu.addAction(makni)
            menu.addSeparator()
            menu.addAction(postavke)
            #connect context menu items
            dodaj.triggered.connect(self.emit_add)
            makni.triggered.connect(self.emit_remove)
            postavke.triggered.connect(self.emit_edit)
        else:
            menu.addAction(dodaj)
            menu.addSeparator()
            menu.addAction(postavke)
            #connect context menu items
            dodaj.triggered.connect(self.emit_add)
            postavke.triggered.connect(self.emit_edit)
        #display context menu
        menu.exec_(self.sender().mapToGlobal(position))

    def find_location_of_sender(self, ref):
        """
        funkcija vraca redak i stupac gdje se nalazi widget koji je pozvao kontekstni
        menu
        """
        rows = self.gridLayout.rowCount()
        cols = self.gridLayout.columnCount()
        for i in range(rows):
            for j in range(cols):
                item = self.gridLayout.itemAtPosition(i, j).widget()
                if item == ref:
                    return i, j
        return None, None

    def emit_add(self, x):
        """
        Metoda emitira zahtjev za dodavanjem nove tocke
        """
        self.emit(QtCore.SIGNAL('addrow'))

    def emit_remove(self, x):
        """
        Metoda emitira zahtjev za brisanjem tocke
        """
        self.emit(QtCore.SIGNAL('removerow(PyQt_PyObject)'), self.redak)

    def emit_edit(self, x):
        """
        Metoda salje zahtjev za promjenom parametara selektirane tocke
        """
        self.emit(QtCore.SIGNAL('editrow(PyQt_PyObject)'), self.redak)

class TablicaKonverterRezultati():

    def __init__(self, parent=None):
        """
        Widget sa tablicom za prikaz rezultata provjere konvertera.
        """
        QtGui.QWidget.__init__(self, parent=parent)
        #bitni memberi
        self.tocke = [] #tocke umjeravanja
        self.data = [] #pandas datafrejm rezultata umjeravanja
        self.jedinica = 'n/a' #string mjerne jedinice

        self.sastavi_inicijalnu_tablicu()

    def set_minimum_width_for_column(self, col, size):
        """
        odredjivanje minimalne sirine stupca
        """
        self.gridLayout.setColumnMinimumWidth(col, size)

    def set_minimum_height_for_row(self, row, size):
        """
        odredjivanje minimalne visine redka
        """
        self.gridLayout.setRowMinimumHeight(row, size)

    def set_mjerna_jedinica(self, jednica):
        """
        setter za mjernu jedinicu
        """
        self.jedinica = jednica
        self.header1.setText("".join(['c, R, NOx\n(', str(self.jedinica), ')']))
        self.header2.setText("".join(['c, R, NO2\n(', str(self.jedinica), ')']))
        self.header3.setText("".join(['c, NO\n(', str(self.jedinica), ')']))
        self.header4.setText("".join(['c, NOx\n(', str(self.jedinica), ')']))

    def set_tocke(self, tocke):
        """
        setter za tocke umjeravanja
        """
        self.tocke = tocke

    def sastavi_inicijalnu_tablicu(self):
        """
        sastavljanje output tablice.
        """
        #definiranje grid layouta
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setHorizontalSpacing(1)
        self.gridLayout.setVerticalSpacing(1)
        self.gridLayout.setContentsMargins(0,0,0,0)
        #headeri
        self.header0 = CustomLabel(tekst='#', center=True)
        self.header1 = CustomLabel(tekst="".join(['c, R, NOx\n(', str(self.jedinica), ')']), center=True)
        self.header2 = CustomLabel(tekst="".join(['c, R, NO2\n(', str(self.jedinica), ')']), center=True)
        self.header3 = CustomLabel(tekst="".join(['c, NO\n(', str(self.jedinica), ')']), center=True)
        self.header4 = CustomLabel(tekst="".join(['c, NOx\n(', str(self.jedinica), ')']), center=True)
        #dodavanje headera u layout
        self.gridLayout.addWidget(self.header0, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.header1, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.header2, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.header3, 0, 3, 1, 1)
        self.gridLayout.addWidget(self.header4, 0, 4, 1, 1)
        #podesavanje horizontalnih dimenzija labela u layoutu za pojedine stupce
        self.set_minimum_width_for_column(0, 30)
        self.set_minimum_width_for_column(1, 75)
        self.set_minimum_width_for_column(2, 75)
        self.set_minimum_width_for_column(3, 75)
        self.set_minimum_width_for_column(4, 75)
        #dodavanje labela sa rezultatima u layout
        #TODO! finish
