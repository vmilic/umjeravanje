# -*- coding: utf-8 -*-
"""
Created on Wed May 20 09:12:51 2015

@author: DHMZ-Milic
"""
import logging
import configparser


class MainKonfig(object):
    """
    Konfig objekt sa glavnim postavkama aplikacije

    error types:
    AttributeError, TypeError
    """
    def __init__(self, cfg):
        logging.info('Pocetak inicijalizacije konfiguracijskog objekta.')
        if not isinstance(cfg, configparser.ConfigParser):
            raise TypeError('Objektu nije prosljedjena instanca ConfigParser.')
        # konfiguracijski objekt
        msg = 'Preuzeta instanca configparsera, self.cfg={0}'.format(cfg)
        logging.debug(msg)
        self.cfg = cfg
        # bitni memberi za umjeravanje
        self.mjerenje = None  # podatak sto se umjerava (header u config objektu NOX,SO2...)
        msg = 'Inicjializacija mjerenja, self.mjerenje={0}'.format(str(self.mjerenje))
        logging.debug(msg)
        self.opseg = 0  # norma: opseg mjerenja ovisno o izabranom mjerenju
        msg = 'Inicjializacija opsega mjerenja, self.opseg={0}'.format(str(self.opseg))
        logging.debug(msg)
        self.dilucija = None  # izabrana dilucijska jedinica (header u config objektu)
        msg = 'Inicjializacija dilucijske jedinice, self.dilucija={0}'.format(str(self.dilucija))
        logging.debug(msg)
        self.cistiZrak = None  # izabrani generator cistog zraka (header u config objektu)
        msg = 'Inicjializacija generatora cistog zraka, self.cistiZrak={0}'.format(str(self.cistiZrak))
        logging.debug(msg)
        self.provjeraLinearnosti = False
        msg = 'Inicjializacija provjere linearnosti, self.provjeraLinearnosti={0}'.format(str(self.provjeraLinearnosti))
        logging.debug(msg)
        self.koncentracijaCRM = 0
        msg = 'Inicjializacija koncenracije CRM-a, self.koncentracijaCRM={0}'.format(str(self.koncentracijaCRM))
        logging.debug(msg)
        self.sljedivostCRM = 0
        msg = 'Inicjializacija sljedivosti CRM-a, self.sljedivostCRM={0}'.format(str(self.sljedivostCRM))
        logging.debug(msg)
        self.cNOX50 = 0
        msg = 'Inicjializacija cNOX50, self.cNOX50={0}'.format(str(self.cNOX50))
        logging.debug(msg)
        self.cNOX95 = 0
        msg = 'Inicjializacija cNOX95, self.cNOX95={0}'.format(str(self.cNOX95))
        logging.debug(msg)
        # REST podaci
        self.uredjajUrl = self.get_konfig_element('REST', 'uredjaj')
        msg = 'Inicijalizacija REST url-a za podatke o mjernim uredjajima, url={0}'.format(self.uredjajUrl)
        logging.info(msg)
        self.postajeUrl = self.get_konfig_element('REST', 'postaje')
        msg = 'Inicijalizacija REST url-a za podatke o postajama, url={0}'.format(self.postajeUrl)
        logging.info(msg)
        # tocke za umjeravanje
        self.umjerneTocke = []
        tocke = self.get_listu_tocaka_za_umjeravanje()
        for tocka in tocke:
            objekt = Tocka(cfg, tocka)
            self.umjerneTocke.append(objekt)
        msg = 'Postavljene tocke za umjeravanje {0}'.format([str(i) for i in self.umjerneTocke])
        logging.info(msg)
        # tocke za provjeru konvertera
        self.konverterTocke = []
        tocke = self.get_listu_tocaka_za_provjeru_konvertera()
        for tocka in tocke:
            objekt = Tocka(cfg, tocka)
            self.konverterTocke.append(objekt)
        msg = 'Postavljene tocke za konverter {0}'.format([str(i) for i in self.konverterTocke])
        logging.info(msg)
        logging.info('Kraj inicijalizacije konfiguracijskog objekta.')

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

    def get_listu_komponenti(self):
        """
        Metoda vraca listu svih komponenti za umjeravanje
        """
        value = self.get_konfig_element('LISTE', 'komponente')
        lista = value.split(sep=',')
        lista = [i.strip() for i in lista]
        return lista

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

    def get_listu_uredjaja(self):
        """
        Metoda vraca listu svih uredjaja.
        """
        value = self.get_konfig_element('LISTE', 'uredjaji')
        lista = value.split(sep=',')
        lista = [i.strip() for i in lista]
        return lista

    def get_listu_komponenti_uredjaja(self, uredjaj):
        """
        Metoda vraca listu svih komponenti za uredjaj.
        """
        value = self.get_konfig_element('UREDJAJI', uredjaj)
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

    def set_mjerenje(self, section):
        """
        Postavljanje izbora mjerenja.
        """
        if self.cfg.has_section(section):
            self.mjerenje = str(section)
            msg = 'Postavljeno novo mjerenje , self.mjerenje={0}'.format(self.mjerenje)
            logging.info(msg)
            self.opseg = self.get_konfig_element(self.mjerenje, 'opseg')
            msg = 'Postavljen novi opseg , self.opseg={0}'.format(self.opseg)
            logging.info(msg)
        else:
            msg = 'Konfiguracijski objekt nema trazeni section, section={0}'.format(section)
            raise AttributeError(msg)


class Tocka(object):
    """
    Podaci o tocki za umjeravanje ili kontrolu konvertera.
    - definiranje slajsa frejma koji predstavlja tocku (min, max, broj zanemarenih)
    -definiranje cref faktora
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
