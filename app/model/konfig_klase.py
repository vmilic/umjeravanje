# -*- coding: utf-8 -*-
"""
Created on Wed May 20 09:12:51 2015

@author: DHMZ-Milic
"""
import logging
import configparser


class BaseKonfig(object):
    """
    Base class for konfig use
    cfg --> ConfigParser object
    sections --> lista (ili bilo koji iterable objekt) sa bitnim sectionima
    """
    def __init__(self, cfg, sections):
        self.cfg = cfg
        self.listaSectiona = sections

    def provjeri_postojanje_elemenata(self):
        """
        Metoda radi grubu provjeru strukture konfig objekta.
        Vraca False ako nesto ne valja, inace vraca True
        """
        if not isinstance(self.cfg, configparser.ConfigParser):
            msg = 'konfig objekt nije instanca ConfigParser, type self.cfg={0}'
            logging.error(msg.format(type(self.cfg)))
            return False
        sec = self.cfg.sections()
        for section in self.listaSectiona:
            if section not in sec:
                msg = 'konfigu nedostaje trazeni section, section={0}'
                logging.error(msg.format(str(section)))
                return False
        return True

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


class MainKonfig(BaseKonfig):
    """
    Konfig objekt sa glavnim postavkama aplikacije
    """
    def __init__(self, cfg):
        requiredSections = ['LISTE',
                            'SO2',
                            'CO',
                            'NOX',
                            'O3',
                            'T700',
                            'ASGU-370',
                            'T701',
                            'T702',
                            'REST']
        BaseKonfig.__init__(self, cfg, requiredSections)

    def get_listu_komponenti(self):
        """
        HELPER, Metoda vraca listu svih komponenti za umjeravanje
        """
        value = self.get_konfig_element('LISTE', 'komponente')
        return value.split(sep=',')

    def get_listu_dilucija(self):
        """
        HELPER, Metoda vraca listu svih dilucija
        """
        value = self.get_konfig_element('LISTE', 'dilucije')
        return value.split(sep=',')

    def get_listu_cistiZrak(self):
        """
        HELPER, Metoda vraca listu svih generatora cistog zraka
        """
        value = self.get_konfig_element('LISTE', 'cisti_zrak')
        return value.split(sep=',')


class UKonfig(BaseKonfig):
    """
    konfig objekt sa 'varijabilnim' podacima za umjeravanje
    """
    def __init__(self, cfg):
        requiredSections = ['TOCKA1',
                            'TOCKA2',
                            'TOCKA3',
                            'TOCKA4',
                            'TOCKA5',
                            'MJERENJE',
                            'KONVERTER',
                            'KTOCKA1',
                            'KTOCKA2',
                            'KTOCKA3',
                            'KTOCKA4',
                            'KTOCKA5',
                            'KTOCKA6']
        BaseKonfig.__init__(self, cfg, requiredSections)

        raspon = self.get_konfig_element('MJERENJE', 'opseg')
        self.set_raspon(raspon)
        cCRM = self.get_konfig_element('MJERENJE', 'koncentracijaCRM')
        self.set_cCRM(cCRM)
        sCRM = self.get_konfig_element('MJERENJE', 'sljedivostCRM')
        self.set_sCRM(sCRM)
        testLinearnost = self.cfg.getboolean('MJERENJE', 'provjeraLinearnosti')
        self.set_testLinearnosti(testLinearnost)
        komponenta = self.get_konfig_element('MJERENJE', 'komponenta')
        self.set_komponenta(komponenta)
        dilucija = self.get_konfig_element('MJERENJE', 'dilucija')
        self.set_dilucija(dilucija)
        cistiZrak = self.get_konfig_element('MJERENJE', 'cistiZrak')
        self.set_cistiZrak(cistiZrak)
        # tocke umjeravanja
        self.tocka1 = Tocka(cfg, 'TOCKA1')
        self.tocka2 = Tocka(cfg, 'TOCKA2')
        self.tocka3 = Tocka(cfg, 'TOCKA3')
        self.tocka4 = Tocka(cfg, 'TOCKA4')
        self.tocka5 = Tocka(cfg, 'TOCKA5')
        logging.debug('postavljanje postavki tocaka za umjeravanje')
        self.tocke = [self.tocka1,
                      self.tocka2,
                      self.tocka3,
                      self.tocka4,
                      self.tocka5]
        # tocke provjere konvertera
        #TODO! nije nuzno da konfig ima membere ispod ako nije NOX
        logging.debug('postavljanje postavki tocaka za provjeru konvertera')
        self.Ktocka1 = Tocka(cfg, 'KTOCKA1')
        self.Ktocka2 = Tocka(cfg, 'KTOCKA2')
        self.Ktocka3 = Tocka(cfg, 'KTOCKA3')
        self.Ktocka4 = Tocka(cfg, 'KTOCKA4')
        self.Ktocka5 = Tocka(cfg, 'KTOCKA5')
        self.Ktocka6 = Tocka(cfg, 'KTOCKA6')
        self.Ktocke = [self.Ktocka1,
                       self.Ktocka2,
                       self.Ktocka3,
                       self.Ktocka4,
                       self.Ktocka5,
                       self.Ktocka6]
        self.cNOX50 = self.get_konfig_element('KONVERTER', 'cNOX50')
        self.cNOX95 = self.get_konfig_element('KONVERTER', 'cNOX95')
        logging.debug('kraj inicijalizacije AppKonfiga')

    def set_raspon(self, value):
        """setter raspona mjerenja"""
        self.raspon = float(value)
        msg = 'raspon mjerenja postavljen, raspon={0}'.format(str(self.raspon))
        logging.debug(msg)

    def set_cCRM(self, value):
        """setter koncentracija Certificiranog Referentnog Materijala"""
        self.cCRM = float(value)
        msg = 'koncentracija CRM postavljea, cCRM={0}'.format(str(self.cCRM))
        logging.debug(msg)

    def set_sCRM(self, value):
        """setter sljedivosti Certificiranog Referentnog Materijala"""
        self.sCRM = float(value)
        msg = 'sljedivost CRM postavljea, sCRM={0}'.format(str(self.sCRM))
        logging.debug(msg)

    def set_testLinearnosti(self, value):
        """setter za provjeru linearnosti (boolean value)"""
        self.testLinearnosti = value
        msg = 'provjera linearnosti, test={0}'.format(str(value))
        logging.debug(msg)

    def set_komponenta(self, value):
        """setter za komponentu"""
        self.izabranaKomponenta = value
        msg = 'komponenta postavljena, komponenta={0}'.format(str(value))
        logging.debug(msg)

    def set_dilucija(self, value):
        """setter za diluciju"""
        self.izabranaDilucija = value
        msg = 'dilucija postavljena, dilucija={0}'.format(str(value))
        logging.debug(msg)

    def set_cistiZrak(self, value):
        """setter za cisti zrak"""
        self.izabraniCistiZrak = value
        msg = 'cisti zrak postavljen, cisti zrak={0}'.format(str(value))
        logging.debug(msg)


class Tocka(object):
    """
    Podaci o tocki, definiranje slajsa frejma koji predstavlja tocku
    """
    def __init__(self, cfg, section):
        OPTIONS = ('startIndeks',
                   'endIndeks',
                   'brojZanemarenih',
                   'crefFaktor')
        self.ime = section
        msg = 'Provjera postojanja opcija, tocka={0}'.format(str(section))
        logging.debug(msg)
        # provjera postojanja svih potrebnih opcija
        for option in OPTIONS:
            if not cfg.has_option(section, option):
                msg = 'Konfigu nedostaje [{0}]:{1}'.format(section, option)
                raise AttributeError(msg)
        self.startIndeks = cfg.getint(section, 'startIndeks')
        msg = '{0} start index set, value={1}'
        logging.debug(msg.format(str(section), str(self.startIndeks)))
        self.endIndeks = cfg.getint(section, 'endIndeks')
        msg = '{0} end index set, value={1}'
        logging.debug(msg.format(str(section), str(self.endIndeks)))
        self.brojZanemarenih = cfg.getint(section, 'brojZanemarenih')
        msg = '{0} broj zanemarenih set, value={1}'
        logging.debug(msg.format(str(section), str(self.brojZanemarenih)))
        self.crefFaktor = cfg.getfloat(section, 'crefFaktor')
        msg = '{0} cref faktor, value={1}'
        logging.debug(msg.format(str(section), str(self.crefFaktor)))
        self.brojPodataka = self.endIndeks - self.startIndeks
        msg = '{0} broj podataka, value={1}'
        logging.debug(msg.format(str(section), str(self.brojPodataka)))

    def index_is_member(self, index):
        """funkcija vraca boolean:
        ako je indeks veci ili jednak startIndeks i manji od endIndex --> True
        svi ostali slucaji --> False
        """
        if index is None:
            return False
        if self.startIndeks is None:
            return False
        if self.endIndeks is None:
            return False
        return index >= self.startIndeks and index < self.endIndeks

    def __str__(self):
        """overloaded string representation"""
        return self.ime
