# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 09:57:44 2016

@author: DHMZ-Milic
"""
import logging
from app.model.komponenta import Komponenta

class Uredjaj(object):
    """
    Reprezentacija mjernog uredjaja.
    Memberi stanja, (sa pripadnim setterima i getterima) su:
    -serial : string, serijskog broja uredjaja
    -proizvodjac : string, naziva proizvodjaca uredjaja
    -oznakaModela : string, oznaka modela uredjaja
    -lokacija : string, naziva lokacije gdje se uredjaj nalazi
    -komponente : mapa, komponente mjerenja
    -analitickeMetode : objekt AnalitickaMetoda

    Postoje dodatne metode za manipulaciju mebmera (dodavanje komponenti, metoda...)
    """
    def __init__(self, serial='n/a', proizvodjac='n/a', oznakaModela='n/a',
                 lokacija='n/a', komponente=None, analitickaMetoda=None):
        self.serial = str(serial)
        self.proizvodjac = str(proizvodjac)
        self.oznakaModela = str(oznakaModela)
        self.lokacija = str(lokacija)
        self.analitickaMetoda = analitickaMetoda
        if komponente == None:
            self.komponente = {}
        else:
            self.set_komponente(komponente)

    def set_serial(self, serial):
        """Setter serijskog broja uredjaja. Input je string."""
        serial = str(serial)
        if serial != self.serial:
            self.serial = serial

    def get_serial(self):
        """Getter serijskog broja uredjaja. Output je string."""
        return self.serial

    def set_proizvodjac(self, proizvodjac):
        """Setter proizvodjaca uredjaja. Input je string."""
        proizvodjac = str(proizvodjac)
        if proizvodjac != self.proizvodjac:
            self.proizvodjac = proizvodjac

    def get_proizvodjac(self):
        """Getter proizvodjaca uredjaja. Output je string."""
        return self.proizvodjac

    def set_oznakaModela(self, oznaka):
        """Setter oznake modela uredjaja. Input je string."""
        oznaka = str(oznaka)
        if oznaka != self.oznakaModela:
            self.oznakaModela = oznaka

    def get_oznakaModela(self):
        """Getter oznake modela uredjaja. Output je string."""
        return self.oznakaModela

    def set_lokacija(self, lokacija):
        """Setter lokacije uredjaja. Input je string."""
        lokacija = str(lokacija)
        if lokacija != self.lokacija:
            self.lokacija = lokacija

    def get_lokacija(self):
        """Getter lokacije uredjaja. Output je string."""
        return self.lokacija

    def set_analitickaMetoda(self, metoda):
        """Setter analiticke metode."""
        self.analitickaMetoda = metoda

    def get_analitickaMetoda(self):
        """Getter analiticke metode"""
        return self.analitickaMetoda

    def set_komponente(self, komponente):
        """Setter mape sa objektima tipa 'Komponenta'. Kljuc u mapi je
        formula pojedinie komponente (npr. 'NO2'). Metoda provjerava da li je
        ulazni parametar mapa i da li su svi elementi mape objekti tipa
        'Komponenta'. Ako nisu, kao komponente se postavlja prazna mapa."""
        test = True
        if isinstance(komponente, dict):
            for komponenta in komponente:
                if not isinstance(komponente[komponenta], Komponenta):
                    self.komponente = {}
                    msg = 'U zadanoj mapi komponente postoje objekti koji nisu tipa "{0}".'.format(str(type(Komponenta)))
                    logging.warning(msg)
                    test=False
                    break
            if test:
                self.komponente = komponente
        else:
            self.komponente = {}
            logging.warning('Ulazni parametar nije mapa. komponente={0}'.format(str(type(komponente))))

    def get_komponente(self):
        """Getter komponenti uredjaja. Output je mapa objekata tipa 'Komponenta' ili
        prazna mapa. Kljucevi mape su formule pojedine komponente"""
        return self.komponente

    def dodaj_komponentu(self, komponenta):
        """Metoda dodaje komponentu u mapu svih komponenti. Ulazni parametar komponenta
        mora biti tipa 'Komponenta'. Kljuc pod kojim se komponenta sprema u mapu je
        formula komponente."""
        if isinstance(komponenta, Komponenta):
            formula = komponenta.get_formula()
            self.komponente[formula] = komponenta

    def izbrisi_komponentu(self, komponenta):
        """Metoda brise komponentu iz mape svih komponenti. Ulazni parametar je string
        kljuca pod kojim je spremljena komponenta (formula)."""
        self.komponente.pop(komponenta, 0) #drugi argument je default za return pop metode

    def set_komponenta_naziv(self, komponenta, naziv):
        """Setter naziva komponente.
        Ulazni parametri su:
        komponenta - string, formula komponente (kljuc u mapi)
        naziv - string, novi naziv
        """
        try:
            self.komponente[komponenta].set_naziv(naziv)
        except Exception as err:
            logging.warning(str(err), exc_info=True)

    def get_komponenta_naziv(self, komponenta):
        """Getter naziva komponente.
        Ulazni parametri su:
        komponenta - string, formula komponente (kljuc u mapi)
        U slucaju pogreske, metoda vraca 'n/a'
        """
        try:
            return self.komponente[komponenta].get_naziv()
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            return 'n/a'

    def set_komponenta_jedinica(self, komponenta, jedinica):
        """Setter mjerne jedinice komponente.
        Ulazni parametri su:
        komponenta - string, formula komponente (kljuc u mapi)
        jedinica - string, nova mjerna jedinica
        """
        try:
            self.komponente[komponenta].set_jedinica(jedinica)
        except Exception as err:
            logging.warning(str(err), exc_info=True)

    def get_komponenta_jedinica(self, komponenta):
        """Getter stringa mjerne jedinice.
        Ulazni parametri su:
        komponenta - string, formula komponente (kljuc u mapi)
        U slucaju pogreske, metoda vraca 'n/a'
        """
        try:
            return self.komponente[komponenta].get_jedinica()
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            return 'n/a'

    def set_komponenta_formula(self, komponenta, formula):
        """Setter stringa formule komponente.
        Ulazni parametri su:
        komponenta - string, formula komponente (kljuc u mapi)
        formula - string, nova formula
        """
        try:
            self.komponente[komponenta].set_formula(formula)
        except Exception as err:
            logging.warning(str(err), exc_info=True)

    def get_komponenta_formula(self, komponenta):
        """Getter stringa formule.
        Ulazni parametri su:
        komponenta - string, formula komponente (kljuc u mapi)
        U slucaju pogreske, metoda vraca 'n/a'
        """
        try:
            return self.komponente[komponenta].get_formula()
        except Exception as err:
            logging.warning(str(err), exc_info=True)
            return 'n/a'

    def get_listu_komponenti(self):
        """Metoda vraca sortiranu listu kljuceva mape sa komponentama."""
        return sorted(list(self.komponente.keys()))
