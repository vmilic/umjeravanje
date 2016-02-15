# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 10:13:19 2016

@author: DHMZ-Milic
"""
import logging
import configparser
import numpy as np
from app.model.tocke import Tocka


class MainKonfig(object):
    """
    Konfig objekt sa glavnim postavkama aplikacije
    """
    def __init__(self, cfg=None, parent=None):
        if not isinstance(cfg, configparser.ConfigParser):
            raise TypeError('MainKonfig objektu nije zadana instanca ConfigParser.')
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
            logging.warning(msg, exc_info=True)
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
            logging.warning(msg, exc_info=True)
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
            logging.warning(msg, exc_info=True)
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
            logging.warning(msg, exc_info=True)
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
        ime = section
        cref = self.cfg.getfloat(section, 'crefFaktor')
        start = self.cfg.getint(section, 'startIndeks')
        end = self.cfg.getint(section, 'endIndeks')
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
            logging.warning(msg)
        objekt = Tocka(ime=ime, start=start, end=end, cref=cref,
                       r=r, g=g, b=b, a=a)
        return objekt
