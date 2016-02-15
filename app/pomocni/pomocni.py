# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 09:27:59 2016

@author: DHMZ-Milic
"""
import requests
import logging
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
from PyQt4 import QtGui, QtCore
from functools import wraps

def activate_wait_spinner(function):
    """dekorator za promjenu cursora u wait cursor prilikom dugotrajnih operacija"""
    @wraps(function)
    def new_func(*args, **kwargs):
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            function(*args, **kwargs)
        except Exception as err:
            #reraise error
            raise err
        finally:
            #return normal cursor shape
            QtGui.QApplication.restoreOverrideCursor()
    return new_func

def pronadji_zero_span(tocke):
    """
    Metoda pronalazi indekse za zero i span.

    Zero je prva tocka koja ima crefFaktor jednak 0.0, a ako niti jedna
    tocka nema taj crefFaktor, onda se uzima ona sa najmanjim crefFaktorom.
    Span je prva tocka sa crefFaktorom 0.8, a ako niti jedna tocka nema
    taj crefFaktor, onda se uzima ona sa najvecim crefFaktorom
    """
    cf = [float(tocka.crefFaktor) for tocka in tocke]
    if 0.0 in cf:
        zero = cf.index(0.0)
    else:
        zero = cf.index(min(cf))
    if 0.8 in cf:
        span = cf.index(0.8)
    else:
        span = cf.index(max(cf))
    return zero, span

def pronadji_zero_span_tocke(tocke):
    """
    metoda vraca tuple zero i span tocke
    """
    zeroIndeks, spanIndeks = pronadji_zero_span(tocke)
    zero = tocke[zeroIndeks]
    span = tocke[spanIndeks]
    return zero, span


def adapt_mjernu_jedinicu(jedinica):
    """konverzija 'u' u utf-8 'mikro' prema potrebi"""
    if jedinica == 'ug/m3':
        return '\u03BCg/m3'
    elif jedinica == 'umol/mol':
        return '\u03BCmol/mol'
    else:
        return jedinica

def get_uredjaje_sa_REST(url):
    """
    Funkcija dohvaca sve uredjaje sa REST servisa. Ulazni parametar je url
    do resursa uredjaji, izlaz je lista svih uredjaja.
    """
    try:
        head = {"accept":"application/xml"}
        r = requests.get(url,
                         headers=head,
                         timeout=15.1)
        if r.ok:
            output = []
            root = ET.fromstring(r.text)
            for uredjaj in root:
                serial = str(uredjaj.find('serijskaOznaka').text)
                output.append(serial)
            return sorted(output)
        else:
            msg = 'Bad request, url={0} , status_code={1}'.format(r.url, r.status_code)
            logging.error(msg)
            return []
    except Exception:
        msg = 'Gruba pogreska kod dohvacanja popisa uredjaja, url={0}'.format(url)
        logging.error(msg, exc_info=True)
        return []

def get_podatke_za_uredjaj_sa_REST(url, serial):
    """
    Metoda dohvaca podatke uredjaja sa REST servisa.
    Input:
    -url do REST resursa uredjaja
    -serijski broj uredjaja
    Output:
    -string (xml struktura preuzeta sa REST-a) ili None u slucaju pogreske prilikom rada
    """
    try:
        combinedUrl = "/".join([url, serial])
        head = {"accept":"application/xml"}
        r = requests.get(combinedUrl,
                         headers=head,
                         timeout=15.1)
        if r.ok:
            return r.text
        else:
            msg = 'Bad request, url={0} , status_code={1}'.format(r.url, r.status_code)
            logging.error(msg)
            return None
    except Exception:
        msg = 'Problem kod dohvacanja informacije o uredjaju, url={0}'.format(combinedUrl)
        logging.error(msg, exc_info=True)
        return None

def get_lokaciju_uredjaja(url, serial):
    """
    Za zadani serijski broj i url (url REST resursa 'uredjaji') dohvaca lokaciju
    uredjaja. U slucaju bilo kakve pogreske sa dohvacanjem podataka, log gresku i vrati 'None'.
    Funkcija vraca string lokacije.
    """
    try:
        relurl = "/".join([url,str(serial),'lokacija'])
        head = {"accept":"application/xml"}
        r = requests.get(relurl,
                         headers=head,
                         timeout=15.1)
        if r.ok and r.status_code != 204:
            root = ET.fromstring(r.text)
            lokacija = root.find('nazivPostaje').text
            return str(lokacija)
        else:
            msg = 'Los request, url={0} , code={1}'.format(r.url, r.status_code)
            logging.error(msg)
            return 'None'
    except Exception:
        msg = 'Pogreska kod trazenja lokacije uredjaja url={0}'.format(relurl)
        logging.error(msg, exc_info=True)
        return 'None'


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


class CustomLabelContext(CustomLabel):
    """
    custom label sa podrskom za kontekstni meni
    """
    def __init__(self, tekst='n/a', center=False, parent=None):
        CustomLabel.__init__(self, tekst=tekst, center=center, parent=parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)


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


class TablicaUmjeravanjeKriterij(QtGui.QWidget):
    """
    Tablica za parametre umjeravanja (kriterij prihvatljivosti)
    [Srs, Srz, rz, rmax, ec]
    ulazni parametrar je nested lista
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent=parent)
        # definicija layouta
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setHorizontalSpacing(1)
        self.gridLayout.setVerticalSpacing(1)
        self.gridLayout.setContentsMargins(0,0,0,0)
        # definicija labela unutar tablice
        # red 0 i granice
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
        self.pos40 = CustomLabel(tekst='<b> 4 </b>', center=True)
        self.pos50 = CustomLabel(tekst='<b> 5 </b>', center=True)
        #red 1
        self.pos11 = CustomLabel()
        self.pos12 = CustomLabel()
        self.pos13 = CustomLabel()
        self.pos14 = CustomLabel()
        self.pos15 = CustomLabel(center=True)
        self.pos16 = CustomLabel(center=True)
        self.red1 = [self.pos10, self.pos11, self.pos12, self.pos13, self.pos14, self.pos15, self.pos16]
        #red 2
        self.pos21 = CustomLabel()
        self.pos22 = CustomLabel()
        self.pos23 = CustomLabel()
        self.pos24 = CustomLabel()
        self.pos25 = CustomLabel(center=True)
        self.pos26 = CustomLabel(center=True)
        self.red2 = [self.pos20, self.pos21, self.pos22, self.pos23, self.pos24, self.pos25, self.pos26]
        #red 3
        self.pos31 = CustomLabel()
        self.pos32 = CustomLabel()
        self.pos33 = CustomLabel()
        self.pos34 = CustomLabel()
        self.pos35 = CustomLabel(center=True)
        self.pos36 = CustomLabel(center=True)
        self.red3 = [self.pos30, self.pos31, self.pos32, self.pos33, self.pos34, self.pos35, self.pos36]
        #red 4
        self.pos41 = CustomLabel()
        self.pos42 = CustomLabel()
        self.pos43 = CustomLabel()
        self.pos44 = CustomLabel()
        self.pos45 = CustomLabel(center=True)
        self.pos46 = CustomLabel(center=True)
        self.red4 = [self.pos40, self.pos41, self.pos42, self.pos43, self.pos44, self.pos45, self.pos46]
        #red 5
        self.pos51 = CustomLabel()
        self.pos52 = CustomLabel()
        self.pos53 = CustomLabel()
        self.pos54 = CustomLabel()
        self.pos55 = CustomLabel(center=True)
        self.pos56 = CustomLabel(center=True)
        self.red5 = [self.pos50, self.pos51, self.pos52, self.pos53, self.pos54, self.pos55, self.pos56]
        self.datarows = [self.red1, self.red2, self.red3, self.red4, self.red5]
        #slaganje labela u grid layout...
        # self.gridLayout.addWidget(widget, row, col, rowspan, colspan)
        self.gridLayout.addWidget(self.pos00, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.pos01, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.pos02, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.pos03, 0, 3, 1, 2)
        self.gridLayout.addWidget(self.pos05, 0, 5, 1, 1)
        self.gridLayout.addWidget(self.pos06, 0, 6, 1, 1)
        self.gridLayout.addWidget(self.pos10, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.pos20, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.pos30, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.pos40, 4, 0, 1, 1)
        self.gridLayout.addWidget(self.pos50, 5, 0, 1, 1)
        for row, labelList in enumerate(self.datarows):
            for col, label in enumerate(self.datarows[row]):
                self.gridLayout.addWidget(label, row+1, col, 1, 1)
        #definiranje minimalne velicine stupaca
        for i in range(7):
            self.set_minimum_height_for_row(i, 30)
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
        for red in range(1, 6):
            self.set_row_background_color(red, QtGui.QColor(QtCore.Qt.white))
            self.set_row_visible(red, True)
        #reset values
        for row in self.datarows:
            for i in range(1, 7):
                row[i].setText('')

    def set_values(self, data):
        """
        setter vrijednosti u tablicu
        ulazni parametar je nested lista s potenicijalno 0 elemenata i max 5.
        svaki element sadrzi listu sa:
        [naziv, tocka norme, kratka oznaka, vrijednost, uvijet prihvatljivosti, ispunjeno]
        """
        self.clear_results()
        red = 1
        for kriterij in data:
            naziv = str(kriterij[0])
            tockaNorme = str(kriterij[1])
            kratkaOznaka = str(kriterij[2])
            vrijednost = str(round(kriterij[3], 1))
            uvjet = str(kriterij[4])
            ispunjeno = str(kriterij[5])
            label = self.datarows[red-1][1]
            label.setText(naziv)
            label = self.datarows[red-1][2]
            label.setText(tockaNorme)
            label = self.datarows[red-1][3]
            label.setText(kratkaOznaka)
            label = self.datarows[red-1][4]
            label.setText(vrijednost)
            label = self.datarows[red-1][5]
            label.setText(uvjet)
            label = self.datarows[red-1][6]
            label.setText(ispunjeno)
            color = self.find_needed_color(ispunjeno)
            self.set_row_background_color(red, color)
            red = red + 1
        for i in range(red, 6):
            self.set_row_visible(i, False)

    def set_row_background_color(self, rowNumber, color):
        """
        metoda za promjenu pozadinske boje reda u tablici
        ulazni parametar je broj reda (int) i boja (QColor)
        """
        if rowNumber in [1, 2, 3, 4, 5]:
            red = self.datarows[rowNumber-1]
            for label in red:
                label.set_color(color)
        else:
            raise ValueError('Nije zadan valjani red')

    def set_row_visible(self, rowNumber, check):
        """
        metoda za sakrivanje reda u tablici (za potrebe provjere linearnosti)
        ulazni parametar je broj reda (int) i boolean koji odredjuje vidljivost
        (True --> visible, False --> hidden)
        """
        if rowNumber in [1, 2, 3, 4, 5]:
            red = self.datarows[rowNumber-1]
            for label in red:
                label.setVisible(check)
        else:
            raise ValueError('Nije zadan valjani red')


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
            self.set_minimum_height_for_row(i+1, 30)
            tocka = self.tocke[i]
            for j in range(7):
                #zapis rednog broja podatka
                if j == 0:
                    txt = str(i+1)
                else:
                    podatak = self.data.iloc[i, j-1] #trazeni element u frejmu
                    podatak = round(podatak, 1)
                    if np.isnan(podatak):
                        #nan slucaj
                        txt = ""
                    elif j == 6 and self.data.iloc[i, 0] == 0:
                        #zero slucaj kod racunanja r, round na 2 decimale
                        p = round(self.data.iloc[i, 5], 2)
                        if np.isnan(p):
                            p=""
                        txt = " ".join([str(p), self.jedinica])
                    else:
                        #normalni slucaj
                        txt = str(podatak)
                lab = CustomLabelContext(tekst=txt)
                #connect signal za custom menu
                lab.customContextMenuRequested.connect(self.contextMenuEvent)
                #boja
                lab.set_color(tocka.get_color())
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
        self.emit(QtCore.SIGNAL('removerow'))

    def emit_edit(self, x):
        """
        Metoda salje zahtjev za promjenom parametara selektirane tocke
        """
        self.emit(QtCore.SIGNAL('editrow'))

    def get_redak(self):
        """
        vraca zadnje zapamceni radak kontekstnog menija
        """
        return self.redak


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

        self.gridLayout.addWidget(self.pos00, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.pos01, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.pos02, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.pos03, 0, 3, 1, 2)
        self.gridLayout.addWidget(self.pos05, 0, 5, 1, 1)
        self.gridLayout.addWidget(self.pos06, 0, 6, 1, 1)
        self.gridLayout.addWidget(self.pos10, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.pos20, 2, 0, 1, 1)
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

        self.set_minimum_height_for_row(0, 30)
        self.set_minimum_height_for_row(1, 30)
        self.set_minimum_height_for_row(2, 30)
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
        #reset color
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

    def set_values(self, data):
        """
        setter vrijednosti u tablicu
        2 reda .... koji idu kao dict... plin:{'rise':[], 'fall':[]}
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
        else:
            pass


class TablicaKonverterRezultati(QtGui.QWidget):

    def __init__(self, parent=None):
        """
        Widget sa tablicom za prikaz rezultata provjere konvertera.
        """
        QtGui.QWidget.__init__(self, parent=parent)
        #bitni memberi
        self.tocke = [] #tocke konvertera
        self.data = [] #pandas datafrejm rezultata konvertera
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

    def set_data(self, frejm):
        """
        setter za podatke
        """
        self.data = frejm
        for row in range(len(frejm)):
            color = self.tocke[row].get_color()
            for col in range(len(frejm.columns)):
                podatak = self.data.iloc[row, col]
                podatak = round(podatak, 1)
                if np.isnan(podatak):
                    podatak = ""
                else:
                    podatak = str(podatak)

                label = self.gridLayout.itemAtPosition(row+1, col+1).widget()
                label.setText(podatak)
                label.set_color(color)

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
        #dodavanje labela sa rezultatima u layout
        for row in range(1, 7):
            for col in range(5):
                if col == 0:
                    label = CustomLabel(tekst=str(row), center=True)
                else:
                    label = CustomLabel(center=True)
                self.gridLayout.addWidget(label, row, col, 1, 1)

        #podesavanje horizontalnih dimenzija labela u layoutu za pojedine stupce
        self.set_minimum_width_for_column(0, 30)
        self.set_minimum_width_for_column(1, 75)
        self.set_minimum_width_for_column(2, 75)
        self.set_minimum_width_for_column(3, 75)
        self.set_minimum_width_for_column(4, 75)
        #podesavanje minimalne visine redaka u layoutu
        for i in range(7):
            self.set_minimum_height_for_row(i, 30)

        self.setLayout(self.gridLayout)


class TablicaKonverterParametri(QtGui.QWidget):
    """
    tablica za prikaz efikasnosti konvertera
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent=parent)

        self.naslov = CustomLabel(tekst='<b> Efikasnost konvertera (%) </b>', center=True)
        self.n0 = CustomLabel(tekst='<b>#</b>', center=True)
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
        self.gridLayout.addWidget(self.n0, 0, 0, 1, 1)
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
        self.valueEc1.setText(str(e1))
        self.valueEc2.setText(str(e2))
        self.valueEc3.setText(str(e3))
        self.valueEc.setText(str(e))

    def reset_value(self):
        """
        reset vrijednosti parametara na 'n/a'
        """
        self.valueEc1.setText('n/a')
        self.valueEc2.setText('n/a')
        self.valueEc3.setText('n/a')
        self.valueEc.setText('n/a')


class TablicaKonverterKriterij(QtGui.QWidget):
    """
    Tablica za prikaz kriterija prilagodbe za konverter

    inicijalno se postavlja prazan... setter uzima listu kao parametar
    [naziv, tocka norme, 'Ec=', vrijednost, uvijet prihvatljivosti, 'DA' ili 'NE']
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
        self.pos11 = CustomLabel()
        self.pos12 = CustomLabel()
        self.pos13 = CustomLabel()
        self.pos14 = CustomLabel()
        self.pos15 = CustomLabel(center=True)
        self.pos16 = CustomLabel(center=True)

        self.gridLayout.addWidget(self.pos00, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.pos01, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.pos02, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.pos03, 0, 3, 1, 2)
        self.gridLayout.addWidget(self.pos05, 0, 5, 1, 1)
        self.gridLayout.addWidget(self.pos06, 0, 6, 1, 1)
        self.gridLayout.addWidget(self.pos10, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.pos11, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.pos12, 1, 2, 1, 1)
        self.gridLayout.addWidget(self.pos13, 1, 3, 1, 1)
        self.gridLayout.addWidget(self.pos14, 1, 4, 1, 1)
        self.gridLayout.addWidget(self.pos15, 1, 5, 1, 1)
        self.gridLayout.addWidget(self.pos16, 1, 6, 1, 1)

        self.set_minimum_height_for_row(0, 30)
        self.set_minimum_height_for_row(1, 30)
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
        self.set_row_background_color(QtGui.QColor(QtCore.Qt.white))
        self.pos11.setText('')
        self.pos12.setText('')
        self.pos13.setText('')
        self.pos14.setText('')
        self.pos15.setText('')
        self.pos16.setText('')

    def set_values(self, data):
        """
        setter vrijednosti u tablicu
        ulazni parametar je nested lista s potenicijalno 0 elemenata i max 5.
        svaki element sadrzi listu sa:
        [naziv, tocka norme, kratka oznaka, vrijednost, uvijet prihvatljivosti, ispunjeno]
        """
        self.clear_results()
        try:
            self.pos11.setText(data[0])
            self.pos12.setText(data[1])
            self.pos13.setText(data[2])
            self.pos14.setText(data[3])
            self.pos15.setText(data[4])
            ispunjeno = data[5]
            self.pos16.setText(ispunjeno)
            color = self.find_needed_color(ispunjeno)
            self.set_row_background_color(color)
        except Exception:
            pass

    def set_row_background_color(self, color):
        """
        metoda za promjenu pozadinske boje reda u tablici
        ulazni parametar je boja (QColor)
        """
        self.pos10.set_color(color)
        self.pos11.set_color(color)
        self.pos12.set_color(color)
        self.pos13.set_color(color)
        self.pos14.set_color(color)
        self.pos15.set_color(color)
        self.pos16.set_color(color)

