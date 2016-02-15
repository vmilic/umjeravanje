# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 10:18:43 2016

@author: DHMZ-Milic
"""
import logging
import numpy as np
from PyQt4 import QtGui


class Tocka(object):
    """Objekt koji definira tocku umjeravanja.
    -ime tocke
    -cref faktor : float u rasponu [0-1], (izrazavanje ref. vrijednosti preko postotka opsega mjerenja)
    -indeksi : set integera, koji definiraju kontinuirani niz indeksa podataka (koji indeksi pripadaju objektu)
    -rgba boje tocke : niz integera u rasponu [0-255]. definira boju
    """
    def __init__(self, ime='TOCKA', start=0, end=0, cref=0.5, r=None, g=None, b=None, a=None):
        self.ime = ime
        self.indeksi = set(range(start, end))
        self.crefFaktor = cref
        #red
        if r:
            if self.is_valid_rgba_value(r):
                self.red = r
            else:
                self.red = np.random.randint(0, high=255)
        else:
            self.red = np.random.randint(0, high=255)
        #green
        if g:
            if self.is_valid_rgba_value(g):
                self.green = g
            else:
                self.green = np.random.randint(0, high=255)
        else:
            self.green = np.random.randint(0, high=255)
        #blue
        if b:
            if self.is_valid_rgba_value(b):
                self.blue = b
            else:
                self.blue = np.random.randint(0, high=255)
        else:
            self.blue = np.random.randint(0, high=255)
        #alpha
        if a:
            if self.is_valid_rgba_value(a):
                self.alpha = a
            else:
                self.alpha = np.random.randint(90, high=150)
        else:
            self.alpha = np.random.randint(90, high=150)

    def set_ime(self, ime):
        """Setter naziva umjerne tocke. Input je string."""
        self.ime = str(ime)

    def get_ime(self):
        """Getter naziva umjerne tocke. Output je string."""
        return self.ime

    def set_indeksi(self, indeksi):
        """Setter indeksa umjerne tocke. Input je set neprekinutih integer
        vrijednosti koji oznacavaju indekse koji pripadaju tocki. npr. {1,2,3,4,5,6}
        znaci da u nekoj listi podataka indeksi [1,6] pripadaju tocki."""
        try:
            self.indeksi = set(indeksi)
        except Exception as err:
            logging.error(str(err), exc_info=True)

    def get_indeksi(self):
        """Getter indeksa umjere tocke. Output je set neperekinutih integer vrijednosti
        (indeksa)."""
        return self.indeksi

    def set_crefFaktor(self, cref):
        """Setter cref parametra. Input je float izmedju [0.0, 1.0]. crefParametar bezdimenzionalni
        faktor koji u umnosku sa opsegom mjerenja daje referentnu kocentraciju za tocku."""
        try:
            cref = float(cref)
            assert ((cref >= 0.0) and (cref <= 1.0)), 'cref mora biti vrijednost izmedju 0.0 i 1.0'
            self.crefFaktor = cref
        except Exception as err:
            logging.warning(str(err), exc_info=True)

    def get_crefFaktor(self):
        """Getter cref parametra. Output je float izmedju [0.0, 1.0]."""
        return self.crefFaktor

    def set_red(self, red):
        """Setter vrijednosti crvene boje (rgba model). Input je integer izmedju [0,255]."""
        try:
            red = int(red)
            if self.is_valid_rgba_value(red):
                self.red = red
        except Exception as err:
            logging.warning(str(err), exc_info=True)

    def get_red(self):
        """Getter vrijednosti crvene boje (rgba model). Output je integer izmedju [0,255]."""
        return self.red

    def set_green(self, green):
        """Setter vrijednosti zelene boje (rgba model). Input je integer izmedju [0,255]."""
        try:
            green = int(green)
            if self.is_valid_rgba_value(green):
                self.green = green
        except Exception as err:
            logging.warning(str(err), exc_info=True)

    def get_green(self):
        """Getter vrijednosti zelene boje (rgba model). Output je integer izmedju [0,255]."""
        return self.green

    def set_blue(self, blue):
        """Setter vrijednosti plave boje (rgba model). Input je integer izmedju [0,255]."""
        try:
            blue = int(blue)
            if self.is_valid_rgba_value(blue):
                self.blue = blue
        except Exception as err:
            logging.warning(str(err), exc_info=True)

    def get_blue(self):
        """Getter vrijednosti plave boje (rgba model). Output je integer izmedju [0,255]."""
        return self.blue

    def set_alpha(self, alpha):
        """Setter vrijednosti transparencije boje (rgba model). Input je integer izmedju [0,255]."""
        try:
            alpha = int(alpha)
            if self.is_valid_rgba_value(alpha):
                self.alpha = alpha
        except Exception as err:
            logging.warning(str(err), exc_info=True)

    def get_alpha(self):
        """Getter vrijednosti transparencije boje (rgba model). Output je integer izmedju [0,255]."""
        return self.alpha

    def set_color(self, r, g, b, a):
        """
        Metoda uzima 4 integer parametra (red, green, blue, alpha) u rasponu od
        [0, 255] i postavlja boju.
        """
        self.set_red(r)
        self.set_green(g)
        self.set_blue(b)
        self.set_alpha(a)

    def get_color(self):
        """
        Metoda vraca QtGui.QColor objekt.
        """
        return QtGui.QColor(self.red, self.green, self.blue, self.alpha)

    def is_valid_rgba_value(self, value):
        """Metoda provjerava da li je vrijednost unutar raspona [0,255] (valid rgba)"""
        if value >= 0 and value <= 255:
            return True
        else:
            return False

    def test_indeks_unutar_tocke(self, indeks):
        """Provjera da li je trazeni indeks unutar indeksa tocke."""
        return indeks in self.indeksi

    def test_indeksi_tocke_se_preklapaju(self, setIndeksa):
        """Provjera da li se indeksi tocke preklapaju sa nekim setom indeksa.
        Ako su indeksi razliciti metoda vraca False. Ako se neki
        indeksi podudaraju, metoda vraca True.

        Trazim duljinu presjeka dva seta indeksa.. output je 0 samo ako se indeksi
        unutar setova razlikuju. funkcija bool samo pretvara rezultat u True / False.
        """
        assert isinstance(setIndeksa, set), 'Ulazni parametar nije tipa set. setIndeksa={0}'.format(str(type(setIndeksa)))
        return bool(len(self.indeksi.intersection(setIndeksa)))

    def __str__(self):
        """String reprezentacija objekta. Output je ime tocke"""
        return self.ime
