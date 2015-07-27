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
        self.provjeraLinearnosti = False
        msg = 'Inicjializacija provjere linearnosti, self.provjeraLinearnosti={0}'.format(str(self.provjeraLinearnosti))
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
        OPTIONS = ('startIndeks',
                   'endIndeks',
                   'brojZanemarenih',
                   'crefFaktor')
        for tocka in tocke:
            for option in OPTIONS:
                if not self.cfg.has_option(str(tocka), option):
                    msg = 'Konfigu nedostaje [{0}]:{1}'.format(str(tocka), option)
                    raise AttributeError(msg)

        for tocka in tocke:
            section = str(tocka)
            objekt = Tocka(ime=section,
                           start=cfg.getint(section, 'startIndeks'),
                           end=cfg.getint(section, 'endIndeks'),
                           ign=cfg.getint(section, 'brojZanemarenih'),
                           cref=cfg.getfloat(section, 'crefFaktor'))
            self.umjerneTocke.append(objekt)

        self.spanTocka = self.umjerneTocke[0]
        self.zeroTocka = self.umjerneTocke[1]
        msg = 'Postavljene zero:{0}i span:{1} tocke.'.format(str(self.zeroTocka), str(self.spanTocka))
        logging.info(msg)
        msg = 'Postavljene tocke za umjeravanje {0}'.format([str(i) for i in self.umjerneTocke])
        logging.info(msg)
        # tocke za provjeru konvertera
        self.konverterTocke = []
        tocke = self.get_listu_tocaka_za_provjeru_konvertera()
        for tocka in tocke:
            for option in OPTIONS:
                if not self.cfg.has_option(str(tocka), option):
                    msg = 'Konfigu nedostaje [{0}]:{1}'.format(str(tocka), option)
                    raise AttributeError(msg)

        for tocka in tocke:
            section = str(tocka)
            objekt = Tocka(ime=section,
                           start=cfg.getint(section, 'startIndeks'),
                           end=cfg.getint(section, 'endIndeks'),
                           ign=cfg.getint(section, 'brojZanemarenih'),
                           cref=cfg.getfloat(section, 'crefFaktor'))
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
    """
    Objekt koji definira tocku mjerenja.

    self.ime --> naziv umjerne tocke
    self.startIndeks --> pocetni indeks od kojeg se uzimaju podaci
    self.endIndeks --> zavrsni indeks do kojeg se uzimaju podaci
    self.brojZanemarenih --> broj zanemarenih indeksa od pocetnog indeksa ( ne ulaze u racunicu)
    self.crefFaktor --> float vrijednost u intervalu 0-1, dodatni parametar tocke vezan za zero i span
    """
    def __init__(self, ime='TOCKA', start=0, end=0, ign=0, cref=1.0):
        self.ime = ime
        self.startIndeks = start
        self.endIndeks = end
        self.brojZanemarenih = ign
        self.crefFaktor = cref
        msg = 'Inicijalizacija instance Tocka sa parametrima ime={0}, start={1}, end={2}, ign={3}, cref={4}'
        msg = msg.format(ime, start, end, ign, cref)
        logging.debug(msg)

    def __str__(self):
        """Metoda vraca ime tocke"""
        return self.ime

    def set_ime(self, ime):
        """Setter za ime tocke"""
        try:
            msg = 'Promjena imena tocke, ime={0}'.format(ime)
            logging.debug(msg)
            self.ime = str(ime)
        except Exception:
            msg = 'Problem kod promjene imena tocke, ime={0}'.format(ime)
            logging.error(msg, exc_info=True)

    def set_crefFaktor(self, x):
        """Setter za cref faktor tocke"""
        try:
            msg = 'Promjena cref tocke, ime={0}, cref={1}'.format(self.ime, x)
            logging.debug(msg)
            self.crefFaktor = float(x)
        except Exception:
            msg = 'Problem kod promjene cref tocke, ime={0}, cref={1}'.format(self.ime, x)
            logging.error(msg, exc_info=True)

    def set_start(self, x):
        """Setter za pocetni indeks"""
        try:
            msg = 'Promjena pocetnog indeksa tocke, ime={0}, start={1}'.format(self.ime, x)
            logging.debug(msg)
            self.startIndeks = int(x)
        except Exception:
            msg = 'Problem kod promjene pocetnog indeksa tocke, ime={0}, start={1}'.format(self.ime, x)
            logging.error(msg, exc_info=True)

    def set_end(self, x):
        """Setter za zavrsni indeks"""
        try:
            msg = 'Promjena zavrsnog indeksa tocke, ime={0}, end={1}'.format(self.ime, x)
            logging.debug(msg)
            self.endIndeks = int(x)
        except Exception:
            msg = 'Problem kod promjene zavrsnog indeksa tocke, ime={0}, end={1}'.format(self.ime, x)
            logging.error(msg, exc_info=True)

    def set_zanemareni(self, x):
        """Setter za broj zanemarenih tocaka"""
        try:
            msg = 'Promjena broja zanemarenih indeksa tocke, ime={0}, ign={1}'.format(self.ime, x)
            logging.debug(msg)
            self.brojZanemarenih = int(x)
        except Exception:
            msg = 'Problem promjene broja zanemarenih indeksa tocke, ime={0}, ign={1}'.format(self.ime, x)
            logging.error(msg, exc_info=True)

    def get_brojPodataka(self):
        """Getter metoda za broj podataka u tocki (ukljucijuci zanemarene)"""
        value = self.endIndeks - self.startIndeks
        msg = 'Ukupan broj podataka, ime={0}, N={1}'.format(self.ime, value)
        logging.debug(msg)
        return value

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


#class Tocka(object):
#    """
#    Podaci o tocki za umjeravanje ili kontrolu konvertera.
#    - definiranje slajsa frejma koji predstavlja tocku (min, max, broj zanemarenih)
#    -definiranje cref faktora
#    """
#    def __init__(self, cfg, section):
#        OPTIONS = ('startIndeks',
#                   'endIndeks',
#                   'brojZanemarenih',
#                   'crefFaktor')
#        self.ime = section
#        msg = 'Provjera postojanja opcija, tocka={0}'.format(str(section))
#        logging.debug(msg)
#        # provjera postojanja svih potrebnih opcija
#        for option in OPTIONS:
#            if not cfg.has_option(section, option):
#                msg = 'Konfigu nedostaje [{0}]:{1}'.format(section, option)
#                raise AttributeError(msg)
#        self.startIndeks = cfg.getint(section, 'startIndeks')
#        msg = '{0} start index set, value={1}'
#        logging.debug(msg.format(str(section), str(self.startIndeks)))
#        self.endIndeks = cfg.getint(section, 'endIndeks')
#        msg = '{0} end index set, value={1}'
#        logging.debug(msg.format(str(section), str(self.endIndeks)))
#        self.brojZanemarenih = cfg.getint(section, 'brojZanemarenih')
#        msg = '{0} broj zanemarenih set, value={1}'
#        logging.debug(msg.format(str(section), str(self.brojZanemarenih)))
#        self.crefFaktor = cfg.getfloat(section, 'crefFaktor')
#        msg = '{0} cref faktor, value={1}'
#        logging.debug(msg.format(str(section), str(self.crefFaktor)))
#        self.brojPodataka = self.endIndeks - self.startIndeks
#        msg = '{0} broj podataka, value={1}'
#        logging.debug(msg.format(str(section), str(self.brojPodataka)))
#
#    def index_is_member(self, index):
#        """funkcija vraca boolean:
#        ako je indeks veci ili jednak startIndeks i manji od endIndex --> True
#        svi ostali slucaji --> False
#        """
#        if index is None:
#            return False
#        if self.startIndeks is None:
#            return False
#        if self.endIndeks is None:
#            return False
#        return index >= self.startIndeks and index < self.endIndeks
#
#    def __str__(self):
#        """overloaded string representation"""
#        return self.ime
