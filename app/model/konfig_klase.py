# -*- coding: utf-8 -*-
"""
Created on Wed May 20 09:12:51 2015

@author: DHMZ-Milic
"""
import configparser
import numpy as np
from PyQt4 import QtGui
import logging


class MainKonfig(object):
    """
    Konfig objekt sa glavnim postavkama aplikacije
    """
    def __init__(self, cfg=None, parent=None):
        if not isinstance(cfg, configparser.ConfigParser):
            raise TypeError('Objektu nije prosljedjena instanca ConfigParser.')
        # konfiguracijski objekt
        self.cfg = cfg
        # REST podaci
        self.uredjajUrl = self.get_konfig_element('REST', 'uredjaj')
        self.postajeUrl = self.get_konfig_element('REST', 'postaje')

    def get_konfig_element(self, section, option):
        """
        Vraca se STRING koji se nalazi u konfig objektu za header i section.
        Ako nedostaje element u konfigu raise Error
        """
        if self.cfg.has_option(section, option):
            return self.cfg.get(section, option)
        else:
            msg = 'Konfigu nedostaje section [{0}], option{1}'.format(section, option)
            raise AttributeError(msg)

    def get_listu_dilucija(self):
        """
        Metoda vraca listu svih dilucijskih jedinica.
        """
        try:
            value = self.get_konfig_element('LISTE', 'dilucije')
            lista = value.split(sep=',')
            lista = [i.strip() for i in lista]
        except AttributeError as err:
            msg = ", ".join([str(err), 'default = []'])
            logging.error(msg, exc_info=True)
            lista = []
        return lista

    def get_listu_cistiZrak(self):
        """
        Metoda vraca listu svih generatora cistog zraka.
        """
        try:
            value = self.get_konfig_element('LISTE', 'cisti_zrak')
            lista = value.split(sep=',')
            lista = [i.strip() for i in lista]
        except AttributeError as err:
            msg = ", ".join([str(err), 'default = []'])
            logging.error(msg, exc_info=True)
            lista = []
        return lista

    def get_listu_tocaka_za_umjeravanje(self):
        """
        Metoda vraca listu svih tocaka za umjeravanje (lista naziva sectiona)
        """
        try:
            value = self.get_konfig_element('LISTE', 'tocke')
            lista = value.split(sep=',')
            lista = [i.strip() for i in lista]
        except AttributeError as err:
            msg = ", ".join([str(err), 'default = []'])
            logging.error(msg, exc_info=True)
            lista = []
        return lista

    def get_listu_tocaka_za_provjeru_konvertera(self):
        """
        Metoda vraca listu svih tocaka za provjeru konvertera (lista naziva
        sectiona u konfiguracijskom fileu).
        """
        try:
            value = self.get_konfig_element('LISTE', 'konverter_tocke')
            lista = value.split(sep=',')
            lista = [i.strip() for i in lista]
        except AttributeError as err:
            msg = ", ".join([str(err), 'default = []'])
            logging.error(msg, exc_info=True)
            lista = []
        return lista

    def log_neispravnu_tocku(self, tocka, option):
        """
        Logging neispravne tocke u clucaju da nedostaje opcija(npr.startIndeks)
        """
        msg = 'U konfiguracijskom fileu tocki "{0}" nedostaje opcija "{1}". Tocka je zanemarena.'.format(str(tocka), option)
        logging.error(msg)

    def get_tockeUmjeravanja(self):
        """
        Metoda vraca listu objekata Tocka (za umjeravanje)
        """
        output = []
        tocke = self.get_listu_tocaka_za_umjeravanje()
        for tocka in tocke:
            section = str(tocka)
            objekt = self.ucitaj_tocku(section)
            if objekt != None:
                output.append(objekt)
        return output

    def get_tockeKonverter(self):
        """
        Metoda vraca listu objekata Tocka (za provjeru konvertera)
        """
        output = []
        tocke = self.get_listu_tocaka_za_provjeru_konvertera()
        for tocka in tocke:
            section = str(tocka)
            objekt = self.ucitaj_tocku(section)
            if objekt != None:
                output.append(objekt)
        return output

    def ucitaj_tocku(self, section):
        """
        Metoda generira objekt Tocka
        """
        if not self.cfg.has_option(section, 'startIndeks'):
            self.log_neispravnu_tocku(section, 'startIndeks')
            return None
        if not self.cfg.has_option(section, 'endIndeks'):
            self.log_neispravnu_tocku(section, 'endIndeks')
            return None
        if not self.cfg.has_option(section, 'crefFaktor'):
            self.log_neispravnu_tocku(section, 'crefFaktor')
            return None
        objekt = Tocka(ime=section,
                       start=self.cfg.getint(section, 'startIndeks'),
                       end=self.cfg.getint(section, 'endIndeks'),
                       cref=self.cfg.getfloat(section, 'crefFaktor'))
        try:
            r = self.cfg.getint(section, 'r')
            g = self.cfg.getint(section, 'g')
            b = self.cfg.getint(section, 'b')
            a = self.cfg.getint(section, 'a')
        except Exception as err:
            r = np.random.randint(low=0, high=255)
            g = np.random.randint(low=0, high=255)
            b = np.random.randint(low=0, high=255)
            a = 90
            msg = str(err) + ', Koristim random boju kao default'
            logging.error(msg, exc_info=True)
        objekt.set_konfig_rgba_color(r, g, b, a)
        return objekt


class Tocka(object):
    """Objekt koji definira tocku mjerenja."""
    def __init__(self, ime='TOCKA', start=0, end=0, cref=0.5):
        self.ime = ime
        self.indeksi = set(range(start, end))
        self.crefFaktor = cref
        r, g, b = list(np.random.randint(0, high=255, size=3))
        self.boja = QtGui.QColor(r, g, b, 90)

    def set_konfig_rgba_color(self, r, g, b, a):
        """setter za boju iz konfig filea"""
        self.boja = QtGui.QColor(r, g, b, a)

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
        return bool(len(self.indeksi.intersection(setIndeksa)))

    def __str__(self):
        """Metoda vraca ime tocke"""
        return self.ime
