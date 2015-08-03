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
    def __init__(self, cfg):
        if not isinstance(cfg, configparser.ConfigParser):
            raise TypeError('Objektu nije prosljedjena instanca ConfigParser.')
        # konfiguracijski objekt
        self.cfg = cfg
        self.provjeraLinearnosti = False
        # REST podaci
        self.uredjajUrl = self.get_konfig_element('REST', 'uredjaj')
        self.postajeUrl = self.get_konfig_element('REST', 'postaje')
        # tocke za umjeravanje
        self.umjerneTocke = []
        tocke = self.get_listu_tocaka_za_umjeravanje()
        msg = 'Lista defaultnih tocaka za umjeravanje, tocke='.format(str(tocke))
        logging.info(msg)
        for tocka in tocke:
            section = str(tocka)
            if not self.cfg.has_option(section, 'startIndeks'):
                self.log_neispravnu_tocku(tocka, 'startIndeks')
                continue  # zanemari tocku
            if not self.cfg.has_option(section, 'endIndeks'):
                self.log_neispravnu_tocku(tocka, 'endIndeks')
                continue  # zanemari tocku
            if not self.cfg.has_option(section, 'crefFaktor'):
                self.log_neispravnu_tocku(tocka, 'crefFaktor')
                continue  # zanemari tocku
            objekt = Tocka(ime=section,
                           start=cfg.getint(section, 'startIndeks'),
                           end=cfg.getint(section, 'endIndeks'),
                           cref=cfg.getfloat(section, 'crefFaktor'))
            self.umjerneTocke.append(objekt)
        # tocke za provjeru konvertera
        self.konverterTocke = []
        tocke = self.get_listu_tocaka_za_provjeru_konvertera()
        msg = 'Lista defaultnih tocaka za provjeru konvertera, tocke='.format(str(tocke))
        logging.info(msg)
        for tocka in tocke:
            section = str(tocka)
            if not self.cfg.has_option(section, 'startIndeks'):
                self.log_neispravnu_tocku(tocka, 'startIndeks')
                continue
            if not self.cfg.has_option(section, 'endIndeks'):
                self.log_neispravnu_tocku(tocka, 'endIndeks')
                continue
            if not self.cfg.has_option(section, 'crefFaktor'):
                self.log_neispravnu_tocku(tocka, 'crefFaktor')
                continue
            objekt = Tocka(ime=section,
                           start=cfg.getint(section, 'startIndeks'),
                           end=cfg.getint(section, 'endIndeks'),
                           cref=cfg.getfloat(section, 'crefFaktor'))
            self.konverterTocke.append(objekt)

    def log_neispravnu_tocku(self, tocka, option):
        """
        Logging neispravne tocke u clucaju da nedostaje opcija(npr.startIndeks)
        """
        msg = 'U konfiguracijskom fileu tocki "{0}" nedostaje opcija "{1}". Tocka je zanemarena.'.format(str(tocka), option)
        logging.error(msg)

    def get_konfig_element(self, section, option):
        """
        Vraca se STRING koji se nalazi u konfig objektu za header i section.
        Ako nedostaje element u konfigu raise Error
        """
        if self.cfg.has_option(section, option):
            return self.cfg.get(section, option)
        else:
            msg = 'Konfigu nedostaje [{0}]:{1}'.format(section, option)
            raise AttributeError(msg)

    def get_listu_dilucija(self):
        """
        Metoda vraca listu svih dilucijskih jedinica.
        """
        value = self.get_konfig_element('LISTE', 'dilucije')
        lista = value.split(sep=',')
        lista = [i.strip() for i in lista]
        return lista

    def get_listu_cistiZrak(self):
        """
        Metoda vraca listu svih generatora cistog zraka.
        """
        value = self.get_konfig_element('LISTE', 'cisti_zrak')
        lista = value.split(sep=',')
        lista = [i.strip() for i in lista]
        return lista

    def get_listu_tocaka_za_umjeravanje(self):
        """
        Metoda vraca listu svih tocaka za umjeravanje (lista naziva sectiona)
        """
        value = self.get_konfig_element('LISTE', 'tocke')
        lista = value.split(sep=',')
        lista = [i.strip() for i in lista]
        return lista

    def get_listu_tocaka_za_provjeru_konvertera(self):
        """
        Metoda vraca listu svih tocaka za provjeru konvertera (lista naziva
        sectiona u konfiguracijskom fileu).
        """
        value = self.get_konfig_element('LISTE', 'konverter_tocke')
        lista = value.split(sep=',')
        lista = [i.strip() for i in lista]
        return lista


class Tocka(object):
    """Objekt koji definira tocku mjerenja."""
    def __init__(self, ime='TOCKA', start=0, end=0, cref=0.5):
        self.ime = ime
        self.indeksi = set(range(start, end))
        self.crefFaktor = cref
        r, g, b = list(np.random.randint(0, high=255, size=3))
        self.boja = QtGui.QColor(r, g, b, 90)

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
