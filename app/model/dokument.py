# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 09:30:52 2016

@author: DHMZ-Milic
"""
import os
import copy
import pickle
import logging
import xml.etree.ElementTree as ET
from PyQt4 import QtGui, QtCore
from app.pomocni import pomocni as helper_funkcije
from app.model.analiticka_metoda import AnalitickaMetoda
from app.model.komponenta import Komponenta
from app.model.dilucijska_jedinica import DilucijskaJedinica
from app.model.generator_cistog_zraka import GeneratorCistogZraka
from app.model.uredjaj import Uredjaj


class Dokument(object):
    """Dokument objekt"""
    def __init__(self, cfg=None):
        self.cfg = cfg  # MainKonfig objekt
        self.komponente = {}
        self.analitickeMetode = {}
        self.dilucijskeJedinice = {}
        self.generatoriCistogZraka = {}
        self.uredjaji = {}
        self.postaje = set()

        self.init_dilucijske_jedinice()
        self.init_generatore_cistog_zraka()
        self.init_podataka_sa_REST()

    def create_local_cache(self):
        """Metoda sprema objekt u file uz pomoc pickle modula. File se
        zove 'local_document_cache.dat' i nalazi se u folderu app/model/"""
        cacheData = {'komponente':self.komponente,
                     'metode':self.analitickeMetode,
                     'dilucije':self.dilucijskeJedinice,
                     'generatori':self.generatoriCistogZraka,
                     'uredjaji':self.uredjaji,
                     'postaje':self.postaje}
        folder = os.path.dirname(__file__)
        path = os.path.join(folder, 'local_document_cache.dat')
        path = os.path.normpath(path)
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        with open(path, mode='wb') as the_file:
            try:
                pickle.dump(cacheData, the_file)
            except Exception as err:
                logging.error(str(err), exc_info=True)
                mes = '\n'.join(['Spremanje REST cache filea nije uspjelo.',str(err)])
                QtGui.QApplication.restoreOverrideCursor()
                QtGui.QMessageBox.warning(QtGui.QApplication, 'Problem', mes)
        QtGui.QApplication.restoreOverrideCursor()

    def load_local_cache(self):
        """Metoda loada postavke iz cache filea u slucaju pogreske prilikom spajanja
        sa REST-om"""
        folder = os.path.dirname(__file__)
        path = os.path.join(folder, 'local_document_cache.dat')
        path = os.path.normpath(path)
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        with open(path, mode='rb') as the_file:
            try:
                mapa = pickle.load(the_file)
                self.komponente = mapa['komponente']
                self.analitickeMetode= mapa['metode']
                self.dilucijskeJedinice = mapa['dilucije']
                self.generatoriCistogZraka = mapa['generatori']
                self.uredjaji = mapa['uredjaji']
                self.postaje = mapa['postaje']
            except Exception as err:
                logging.error(str(err), exc_info=True)
                mes = '\n'.join(['Ucitavanje REST cache nije uspjelo.', str(err)])
                QtGui.QApplication.restoreOverrideCursor()
                QtGui.QMessageBox.warning(QtGui.QApplication, 'Problem', mes)
        QtGui.QApplication.restoreOverrideCursor()
################################################################################
    #postaje -- set stringova
    def get_listu_postaja(self):
        """getter sorted liste postaja u dokumentu"""
        popis = sorted(list(self.postaje))
        return popis

    def add_postaju(self, x):
        """Dodavanje postaje na popis, ulazni parametar je string"""
        value = str(x)
        self.postaje.add(value)
################################################################################
    #komponente
    def get_listu_komponenti(self):
        """Getter liste komponenti u dokumentu"""
        popis = sorted(list(self.komponente.keys()))
        return popis

    def get_komponentu(self, naziv):
        """Getter komponente iz dokumenta"""
        return self.komponente[naziv]

    def get_kopiju_komponente(self, naziv):
        """Getter kopije komponente iz dokumenta"""
        komponenta = copy.deepcopy(self.komponente[naziv])
        return komponenta

    def set_novu_komponentu(self, naziv, komponenta):
        """Setter komponente u dokument"""
        if naziv not in self.komponente.keys():
            self.komponente[naziv] = komponenta
################################################################################
    #analiticke metode
    def get_listu_analitickih_metoda(self):
        """Getter liste analitickih metoda u dokumentu"""
        popis = sorted(list(self.analitickeMetode.keys()))
        return popis

    def get_analiticku_metodu(self, naziv):
        """Getter analiticke metode iz dokumenta"""
        return self.analitickeMetode[naziv]

    def get_kopiju_analiticke_metode(self, naziv):
        """Getter kopije analiticke metode iz dokumenta"""
        metoda = copy.deepcopy(self.analitickeMetode[naziv])
        return metoda

    def set_novu_analiticku_metodu(self, naziv, metoda):
        """Setter analiticke metode u dokument"""
        if naziv not in self.analitickeMetode.keys():
            self.analitickeMetode[naziv] = metoda
################################################################################
    #kalibracijske jedinice
    def init_dilucijske_jedinice(self):
        """Metoda inicijalizira dilucijske jedinice koristeci konfig file. Dilucijske
        jedinice postavlja u mapu self.dilucijskeJedinice (kljuc u mapi je model dilucijske
        jedinice)."""
        dilucije = self.cfg.get_listu_dilucija()
        for dilucija in dilucije:
            unit = self.load_dilucijsku_jedinicu_iz_konfiga(dilucija)
            self.dilucijskeJedinice[dilucija] = unit

    def load_dilucijsku_jedinicu_iz_konfiga(self, model):
        """
        Za zadani model dilucijske jedinice, metoda vraca objekt 'DilucijskaJedinica'
        sa podacima ucitanim iz glavnog konfig objekta. U slucaju da u konfigu nedostaju
        podaci koriste se defaulti ('n/a' i np.NaN)
        """
        unit = DilucijskaJedinica(model=model)
        try:
            proizvodjac = self.cfg.get_konfig_element(model, 'proizvodjac')
            unit.set_proizvodjac(proizvodjac)
        except Exception as err:
            logging.warning(str(err))
        try:
            uNul = float(self.cfg.get_konfig_element(model, 'MFC_NUL_PLIN_U'))
            unit.set_uNul(uNul)
        except Exception as err:
            logging.warning(str(err))
        try:
            uKal = float(self.cfg.get_konfig_element(model, 'MFC_KAL_PLIN_U'))
            unit.set_uKal(uKal)
        except Exception as err:
            logging.warning(str(err))
        try:
            uO3 = float(self.cfg.get_konfig_element(model, 'GENERATOR_OZONA_U'))
            unit.set_uO3(uO3)
        except Exception as err:
            logging.warning(str(err))
        try:
            sljedivost = self.cfg.get_konfig_element(model, 'sljedivost')
            unit.set_sljedivost(sljedivost)
        except Exception as err:
            logging.warning(str(err))
        return unit

    def get_listu_dilucijskih_jedinica(self):
        """Getter liste dilucijskih jedinica u dokumentu"""
        popis = sorted(list(self.dilucijskeJedinice.keys()))
        return popis

    def get_diluciju(self, naziv):
        """Getter dilucijske jedinice iz dokumenta"""
        jedinica = self.dilucijskeJedinice[naziv]
        assert isinstance(jedinica, DilucijskaJedinica), 'U mapi dilucijskih jedinica, pod kljucem {0}, nije objekt klase "DilucijskaJedinica"'.format(str(naziv))
        return jedinica

    def get_kopiju_dilucije(self, naziv):
        """Getter kopije dilucijske jedinice iz dokumenta"""
        jedinica = self.dilucijskeJedinice[naziv]
        jedinica = copy.deepcopy(jedinica)
        assert isinstance(jedinica, DilucijskaJedinica), 'U mapi dilucijskih jedinica, pod kljucem {0}, nije objekt klase "DilucijskaJedinica"'.format(str(naziv))
        return jedinica

    def set_diluciju(self, naziv, jedinica):
        """Setter dilucijske jedinice u dokument"""
        self.dilucijskeJedinice[naziv] = jedinica

    def remove_diluciju(self, naziv):
        """Metoda brise dilucijsku jedinicu iz dokumenta"""
        self.dilucijskeJedinice.pop(naziv, 0)
################################################################################
    #generatori cistog zraka
    def init_generatore_cistog_zraka(self):
        """Metoda inicijalizira generatore cistog zraka koristeci podatke iz konfig
        filea. Generatore postavlja u mapu self.generatoriCistogZraka (kljuc je model
        generatora cistog zraka)."""
        generatori = self.cfg.get_listu_cistiZrak()
        for generator in generatori:
            unit = self.load_generator_cistog_zraka_iz_konfiga(generator)
            self.generatoriCistogZraka[generator] = unit

    def load_generator_cistog_zraka_iz_konfiga(self, model):
        """
        Za zadani model generatora cistog zraka, metoda vraca objekt 'GeneratorCistogZraka'
        sa podacima ucitanim iz glavnog konfig objekta. U slucaju da u konfigu nedostaju
        podaci koriste se defaulti ('n/a' i np.NaN)
        """
        unit = GeneratorCistogZraka(model=model)
        try:
            proizvodjac = self.cfg.get_konfig_element(model, 'proizvodjac')
            unit.set_proizvodjac(proizvodjac)
        except Exception as err:
            logging.warning(str(err))
        try:
            maxO3 = float(self.cfg.get_konfig_element(model, 'O3'))
            unit.set_maxO3(maxO3)
        except Exception as err:
            logging.warning(str(err))
        try:
            maxBTX = float(self.cfg.get_konfig_element(model, 'BTX'))
            unit.set_maxBTX(maxBTX)
        except Exception as err:
            logging.warning(str(err))
        try:
            maxCO = float(self.cfg.get_konfig_element(model, 'CO'))
            unit.set_maxCO(maxCO)
        except Exception as err:
            logging.warning(str(err))
        try:
            maxSO2 = float(self.cfg.get_konfig_element(model, 'SO2'))
            unit.set_maxSO2(maxSO2)
        except Exception as err:
            logging.warning(str(err))
        try:
            maxNOx = float(self.cfg.get_konfig_element(model, 'NOx'))
            unit.set_maxNOx(maxNOx)
        except Exception as err:
            logging.warning(str(err))
        return unit

    def get_listu_generatora_cistog_zraka(self):
        """Getter liste generatora cistog zraka iz dokumentu"""
        popis = sorted(list(self.generatoriCistogZraka.keys()))
        return popis

    def get_cistiZrak(self, naziv):
        """Getter generatora cistog zraka iz dokumenta."""
        cistiZrak = self.generatoriCistogZraka[naziv]
        assert isinstance(cistiZrak, GeneratorCistogZraka), 'U mapi generatora cistog zraka, pod kljucem {0}, nije objekt klase "GeneratorCistogZraka"'.format(str(naziv))
        return cistiZrak

    def get_kopiju_cistiZrak(self, naziv):
        """Getter kopije generatora cistog zraka iz dokumenta."""
        cistiZrak = self.generatoriCistogZraka[naziv]
        cistiZrak = copy.deepcopy(cistiZrak)
        assert isinstance(cistiZrak, GeneratorCistogZraka), 'U mapi generatora cistog zraka, pod kljucem {0}, nije objekt klase "GeneratorCistogZraka"'.format(str(naziv))
        return cistiZrak

    def set_cistiZrak(self, naziv, cistiZrak):
        """Setter generatora cistog zraka u dokument"""
        self.generatoriCistogZraka[naziv] = cistiZrak

    def remove_cistiZrak(self, naziv):
        """Metoda brise generator cistog zraka iz dokumenta"""
        self.generatoriCistogZraka.pop(naziv, 0)
################################################################################
    #uredjaji
    def init_podataka_sa_REST(self):
        """
        Metoda inicijalizira uredaje, analiticke metode i komponente koristeci
        podatke sa REST-a. Mapa analitickih metoda i mapa komponenti se postepeno
        nadopunjava sa podacima od pojedinog uredjaja.
        """
        urlUredjaj = self.cfg.get_konfig_element('REST', 'uredjaj')
        listaUredjaja = helper_funkcije.get_uredjaje_sa_REST(urlUredjaj)
        #inicijalizacija svih dostupnih uredjaja
        if listaUredjaja:
            for uredjaj in listaUredjaja:
                UNIT = Uredjaj(serial=uredjaj)
                tekst = helper_funkcije.get_podatke_za_uredjaj_sa_REST(urlUredjaj, uredjaj)
                #ako postoje podaci za uredjaj
                if tekst:
                    try:
                        root = ET.fromstring(tekst)
                        #OSNOVNI PODACI UREDJAJA
                        try:
                            lokacija = helper_funkcije.get_lokaciju_uredjaja(urlUredjaj, uredjaj)
                            UNIT.set_lokacija(lokacija)
                            self.add_postaju(lokacija)
                        except Exception:
                            pass
                        try:
                            proizvodjac = root.find('modelUredjajaId/proizvodjacId/naziv').text
                            UNIT.set_proizvodjac(proizvodjac)
                        except Exception:
                            pass
                        try:
                            oznakaModela = root.find('modelUredjajaId/oznakaModela').text
                            UNIT.set_oznakaModela(oznakaModela)
                        except Exception:
                            pass
                        #ANALITICKA METODA
                        METODA = AnalitickaMetoda()
                        try:
                            ID = root.find('./modelUredjajaId/analitickeMetodeId/id').text
                            METODA.set_ID(ID)
                        except Exception:
                            pass
                        try:
                            norma = root.find('./modelUredjajaId/analitickeMetodeId/norma').text
                            METODA.set_norma(norma)
                        except Exception:
                            pass
                        try:
                            naziv = root.find('./modelUredjajaId/analitickeMetodeId/naziv').text
                            METODA.set_naziv(naziv)
                        except Exception:
                            pass
                        #elementi za racunanje...(Srz, Srs, rz, rmax...)
                        try:
                            metode = root.find('./modelUredjajaId/analitickeMetodeId')
                            for granica in metode.findall('dozvoljeneGraniceCollection'):
                                try:
                                    oznaka = granica.find('./ispitneVelicine/oznaka').text
                                    value = granica.find('max').text
                                    if oznaka == 'o':
                                        METODA.set_o(value)
                                        #pokusaj dolaska do mjerne jedinice
                                        jedinica = granica.find('./mjerneJediniceId/oznaka').text
                                        jedinica = helper_funkcije.adapt_mjernu_jedinicu(jedinica)
                                        METODA.set_jedinica(jedinica)
                                    elif oznaka == 'Ec':
                                        #za efikasnost konvertera treba i min granica
                                        METODA.set_Ec_max(value)
                                        minvalue = granica.find('min').text
                                        METODA.set_Ec_min(minvalue)
                                    else:
                                        METODA.set_member[oznaka](value)
                                except Exception:
                                    pass
                        except Exception:
                            pass
                        #ako metoda ne postoji na popisu... dodaj ju
                        self.set_novu_analiticku_metodu(ID, METODA)
                        #postavi analiticku metodu u uredjaj
                        UNIT.set_analitickaMetoda(METODA)
                        #KOMPONENTE UREDJAJA
                        try:
                            komponente = root.find('modelUredjajaId')
                            for komponenta in komponente.findall('komponentaCollection'):
                                KOMPONENTA = Komponenta()
                                try:
                                    formula = komponenta.find('formula').text
                                    KOMPONENTA.set_formula(formula)
                                    naziv = komponenta.find('naziv').text
                                    KOMPONENTA.set_naziv(naziv)
                                    mjernaJedinica = komponenta.find('./mjerneJediniceId/oznaka').text
                                    mjernaJedinica = helper_funkcije.adapt_mjernu_jedinicu(mjernaJedinica)
                                    KOMPONENTA.set_jedinica(mjernaJedinica)
                                    kv = komponenta.find('konvVUM').text
                                    KOMPONENTA.set_kv(kv)
                                    #dodaj komponentu u mapu
                                    self.set_novu_komponentu(formula, KOMPONENTA)
                                    #dodaj komponentu u uredjaj
                                    UNIT.dodaj_komponentu(KOMPONENTA)
                                except Exception:
                                    pass
                        except Exception:
                            pass
                        #postavi uredjaj u mapu sa serijskim uredjajima
                        self.dodaj_uredjaj(uredjaj, UNIT)
                    except Exception as err:
                        logging.warning(str(err))
            self.create_local_cache()
        else:
            self.load_local_cache()

    def get_listu_uredjaja(self):
        """Getter liste definiranih uredjaja iz dokumenta"""
        lista = sorted(list(self.uredjaji.keys()))
        return lista

    def get_uredjaj(self, naziv):
        """Getter uredjaja iz dokumenta"""
        ure = self.uredjaji[naziv]
        assert isinstance(ure, Uredjaj), 'U mapi uredjaja, pod kljucem {0}, nije objekt klase "Uredjaj"'.format(str(naziv))
        return ure

    def get_kopiju_uredjaja(self, naziv):
        """Getter kopije uredjaja iz dokumenta"""
        ure = self.uredjaji[naziv]
        ure = copy.deepcopy(ure)
        assert isinstance(ure, Uredjaj), 'U mapi uredjaja, pod kljucem {0}, nije objekt klase "Uredjaj"'.format(str(naziv))
        return ure

    def dodaj_uredjaj(self, naziv, ure):
        """Setter uredjaja u dokument"""
        self.uredjaji[naziv] = ure

    def remove_uredjaj(self, naziv):
        """Metoda brise uredjaj iz dokumenta"""
        self.uredjaji.pop(naziv, 0)
################################################################################
